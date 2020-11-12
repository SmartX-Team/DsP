#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>
#include <linux/bpf.h>

#define ETH_DOT1Q
#define IP_TCP 6
#define IP_UDP 17
#define IP_ICMP4 1

#define ETH_HLEN 14
#define DOT1Q_HLEN 4
#define UDP_HLEN 8
#define ICMP4_HLEN 8
#define VXLAN_HLEN 8

struct flow_tuple_t {
    u32 dip;
    u32 sip;
    u16 dport;
    u16 sport;
    u8 l4_proto;
};

struct flow_stat_t{
    u32 flow_cnt;
    u32 flow_bytes;
};

BPF_PERF_OUTPUT(skb_events);    // has to be delcared outside any function
BPF_HASH(<map_name>, struct flow_tuple_t, struct flow_stat_t, 256); // let's try to save the number of IPs in here

int packet_measure(struct __sk_buff *skb) {
    u8 *cursor = 0;

    //
    // All Measurement Metrics
    //

    // For the five tuples
    struct flow_tuple_t flow_tuple = {0};
    struct flow_stat_t *flow_stat;

    // For Overlay Virtual Networks
    u32 vsip = 0, vdip = 0, vni = 0;
    u16 vsport = 0, vdport = 0, vlanid = 0;

    // Other metrics
    u32 tcp_wlen = 0, pkt_len = 0;
    u8 ip_ver = 0;

    u32 p_off = 0;
    u32 p_len = 0;

    u32 *count = 0;
    u32 one = 1;

    ETH: {
        struct ethernet_t *ethernet = cursor_advance(cursor, sizeof(*ethernet));  // ethernet header (frame)
        p_off += ETH_HLEN;
        pkt_len += ETH_HLEN;

        //filter IP packets (ethernet type = 0x0800) 0x0800 is IPv4 packet
        switch(ethernet->type){
            case ETH_P_8021Q:   goto DOT1Q;
            case ETH_P_IP:      goto IPV4;
            default:            goto DROP;
        }
    }

    DOT1Q: {
        struct dot1q_t *dot1q = cursor_advance(cursor, sizeof(*dot1q));
        p_off += DOT1Q_HLEN;
        pkt_len += ETH_HLEN;

        vlanid = dot1q -> vlanid;
        goto IPV4;
    }

    IPV4: {
        struct ip_t *ip = cursor_advance(cursor, sizeof(*ip));	// IP header (datagram)
        /*
          calculate ip header length
          value to multiply * 4
          e.g. ip->hlen = 5 ; IP Header Length = 5 x 4 byte = 20 byte
          The minimum value for this field is 5, which indicates a length of 5 x 32 bits(4 bytes) = 20 bytes
        */
        p_off += ip->hlen << 2;    //SH L 2 -> *4 multiply
        p_len = ip->tlen  - (ip->hlen << 2);
        pkt_len += ip->tlen;

        flow_tuple.dip = ip -> dst;
        flow_tuple.sip = ip -> src;
        flow_tuple.l4_proto = ip -> nextp;

        switch(flow_tuple.l4_proto){
            case IP_TCP:    goto TCP;
            case IP_UDP:    goto UDP;
            case IP_ICMP4:  goto ICMP4;
            default:        goto DROP;
        }
    }

    ICMP4: {
        //  This version does not handle ICMP4 headers
        p_off += ICMP4_HLEN;
        p_len -= ICMP4_HLEN;
        goto STORE;
    }

    UDP: {
        struct udp_t *udp = cursor_advance(cursor, sizeof(*udp));
        p_off += UDP_HLEN;
        p_len -= UDP_HLEN;

        flow_tuple.dport = udp -> dport;
        flow_tuple.sport = udp -> sport;

        // if something -> goto VXLAN
        switch(flow_tuple.dport){
            case 4789:  goto VXLAN;
            default:    goto PAYLOAD;
        }
    }

    TCP: {
        struct tcp_t *tcp = cursor_advance(cursor, sizeof(*tcp));
        /*
          calculate tcp header length
          value to multiply *4
          e.g. tcp->offset = 5 ; TCP Header Length = 5 x 4 byte = 20 byte
          The minimum value for this field is 5, which indicates a length of 5 x 32 bits(4 bytes) = 20 bytes
        */
        p_off += tcp -> offset << 2; //SHL 2 -> *4 multiply
        p_len -= tcp -> offset << 2;

        flow_tuple.dport = tcp -> dst_port;
        flow_tuple.sport = tcp -> src_port;
        tcp_wlen = tcp -> rcv_wnd;

        goto PAYLOAD;
    }

    VXLAN: {
        struct vxlan_t *vxlan = cursor_advance(cursor, sizeof(*vxlan));
        p_off += VXLAN_HLEN;
        vni = vxlan -> key;
        goto VXLAN_ETH;
    }

    VXLAN_ETH: {
        struct ethernet_t *vxlan_ethernet = cursor_advance(cursor, sizeof(*vxlan_ethernet));
        p_off += ETH_HLEN;
        goto VXLAN_IP;
    }

    VXLAN_IP: {
        struct ip_t *vxlan_ip = cursor_advance(cursor, sizeof(*vxlan_ip));
        p_off += vxlan_ip -> hlen << 2;
        p_len = vxlan_ip->tlen - (vxlan_ip->hlen << 2);

        switch(vxlan_ip->nextp){
            case IP_TCP:    goto VXLAN_TCP;
            case IP_UDP:    goto VXLAN_UDP;
            case IP_ICMP4:  goto VXLAN_ICMP4;
            default:        goto DROP;
        }
    }

    VXLAN_UDP: {
        struct udp_t *vxlan_udp = cursor_advance(cursor, sizeof(*vxlan_udp));
        p_off += UDP_HLEN;
        p_len -= UDP_HLEN;

        vdport = vxlan_udp -> dport;
        vsport = vxlan_udp -> sport;
    }

    VXLAN_TCP: {
        struct tcp_t *vxlan_tcp = cursor_advance(cursor, sizeof(*vxlan_tcp));
        /*
          calculate tcp header length
          value to multiply *4
          e.g. tcp->offset = 5 ; TCP Header Length = 5 x 4 byte = 20 byte
          The minimum value for this field is 5, which indicates a length of 5 x 32 bits(4 bytes) = 20 bytes
        */
        p_off += vxlan_tcp -> offset << 2; //SHL 2 -> *4 multiply
        p_len -= vxlan_tcp -> offset << 2;

        vdport = vxlan_tcp -> dst_port;
        vsport = vxlan_tcp -> src_port;
        tcp_wlen = vxlan_tcp -> rcv_wnd;

        goto PAYLOAD;
    }

    VXLAN_ICMP4: {
        p_off += ICMP4_HLEN;
        p_len -= ICMP4_HLEN;
        goto STORE;
    }

    PAYLOAD: {
        /*
          http://stackoverflow.com/questions/25047905/http-request-minimum-size-in-bytes
          minimum length of http request is always greater than 7 bytes
          avoid invalid access memory
          include empty payload
        */
        if(p_len < 7) {
            goto DROP;
        }

        /*
          load first 7 byte of payload into p (payload_array)
          direct access to skb not allowed
          load_byte(): read binary data from socket buffer(skb)
        */
        unsigned long p[7];
        int i = 0;
        int j = 0;
        for (i = p_off ; i < (p_off + 7) ; i++) {
            p[j] = load_byte(skb , i);
            j++;
        }
    }

	STORE: {
	    flow_stat = <map_name>.lookup(&flow_tuple); // this prevents transmitted packets from being counted
	    if (flow_stat) {
	        flow_stat->flow_cnt += 1;
	        flow_stat->flow_bytes += pkt_len;
	    } else {
	        struct flow_stat_t tmp_flow_stat = {.flow_cnt = 1, .flow_bytes = pkt_len};
	        <map_name>.update(&flow_tuple, &tmp_flow_stat);
	    }
//        count = <map_name>.lookup(&flow_tuple); // this prevents transmitted packets from being counted
//        if (count) {
//            // check if this map exists
//            *count += 1;
//        } else {
//            <map_name>.update(&flow_tuple, &one);
//        }
    }

	DROP:
        return -1;
}

//struct ethernet_t {
//  unsigned long long  dst:48;
//  unsigned long long  src:48;
//  unsigned int        type:16;
//} BPF_PACKET_HEADER;

//struct dot1q_t {
//  unsigned short pri:3;
//  unsigned short cfi:1;
//  unsigned short vlanid:12;
//  unsigned short type;
//} BPF_PACKET_HEADER;

//struct ip_t {
//  unsigned char   ver:4;           // byte 0
//  unsigned char   hlen:4;
//  unsigned char   tos;
//  unsigned short  tlen;
//  unsigned short  identification; // byte 4
//  unsigned short  ffo_unused:1;
//  unsigned short  df:1;
//  unsigned short  mf:1;
//  unsigned short  foffset:13;
//  unsigned char   ttl;             // byte 8
//  unsigned char   nextp;
//  unsigned short  hchecksum;
//  unsigned int    src;            // byte 12
//  unsigned int    dst;            // byte 16
//} BPF_PACKET_HEADER;

//struct icmp_t {
//  unsigned char   type;
//  unsigned char   code;
//  unsigned short  checksum;
//} BPF_PACKET_HEADER;

//struct udp_t {
//  unsigned short sport;
//  unsigned short dport;
//  unsigned short length;
//  unsigned short crc;
//} BPF_PACKET_HEADER;

//struct tcp_t {
//  unsigned short  src_port;   // byte 0
//  unsigned short  dst_port;
//  unsigned int    seq_num;    // byte 4
//  unsigned int    ack_num;    // byte 8
//  unsigned char   offset:4;    // byte 12
//  unsigned char   reserved:4;
//  unsigned char   flag_cwr:1;
//  unsigned char   flag_ece:1;
//  unsigned char   flag_urg:1;
//  unsigned char   flag_ack:1;
//  unsigned char   flag_psh:1;
//  unsigned char   flag_rst:1;
//  unsigned char   flag_syn:1;
//  unsigned char   flag_fin:1;
//  unsigned short  rcv_wnd;
//  unsigned short  cksum;      // byte 16
//  unsigned short  urg_ptr;
//} BPF_PACKET_HEADER;

//struct vxlan_t {
//  unsigned int rsv1:4;
//  unsigned int iflag:1;
//  unsigned int rsv2:3;
//  unsigned int rsv3:24;
//  unsigned int key:24;
//  unsigned int rsv4:8;
//} BPF_PACKET_HEADER;

