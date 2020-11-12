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
    u32 start_time;
    u32 end_time;

    u16 spkt_cnt;
    u16 dpkt_cnt;
    u16 spkt_byte;
    u16 dpkt_byte;

    u16 syn_cnt;
    u16 ack_cnt;
    u16 rst_cnt;
    u16 fin_cnt;
};

BPF_PERF_OUTPUT(skb_events);    // has to be delcared outside any function
BPF_HASH(<map_name>, struct flow_key_t, struct flow_info_t); // let's try to save the number of IPs in here

int packet_measure(struct __sk_buff *skb) {
    u8 *cursor = 0;

    struct flow_tuple_t flow_tuple = {0};
    struct flow_stat_t *flow_stat;

    u32 pkt_len = 0;
    u8 tcp_cwr, tcp_ece, tcp_urg, tcp_ack, tcp_psh, tcp_rst, tcp_syn, tcp_fin;

    // Other metrics
    // Current time
    // Packet length

    ETH: {
        struct ethernet_t *ethernet = cursor_advance(cursor, sizeof(*ethernet));  // ethernet header (frame)
        payload_offset += ETH_HLEN;
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
        payload_offset += DOT1Q_HLEN;
        pkt_len += DOT1Q_HLEN;

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
        payload_offset += ICMP4_HLEN;
        payload_length -= ICMP4_HLEN;
        goto STORE;
    }

    UDP: {
        struct udp_t *udp = cursor_advance(cursor, sizeof(*udp));
        payload_offset += UDP_HLEN;
        payload_length -= UDP_HLEN;

        flow_tuple.dport = udp -> dport;
        flow_tuple.sport = udp -> sport;

        goto STORE;
    }

    TCP: {
        struct tcp_t *tcp = cursor_advance(cursor, sizeof(*tcp));
        /*
          calculate tcp header length
          value to multiply *4
          e.g. tcp->offset = 5 ; TCP Header Length = 5 x 4 byte = 20 byte
          The minimum value for this field is 5, which indicates a length of 5 x 32 bits(4 bytes) = 20 bytes
        */
        payload_offset += tcp -> offset << 2; //SHL 2 -> *4 multiply
        payload_length -= tcp -> offset << 2;

        flow_tuple.dport = tcp -> dst_port;
        flow_tuple.sport = tcp -> src_port;

        tcp_cwr = tcp -> flag_cwr;
        tcp_ece = tcp -> flag_ece;
        tcp_urg = tcp -> flag_urg;
        tcp_ack = tcp -> flag_ack;
        tcp_psh = tcp -> flag_psh;
        tcp_rst = tcp -> flag_rst;
        tcp_syn = tcp -> flag_syn;
        tcp_fin = tcp -> flag_fin;

        goto STORE;
    }

	STORE: {
	    struct flow_tuple_t rev_flow_tuple = {
	        dip = flow_tuple -> dip;
            sip = flow_tuple -> sip;
            dport = flow_tuple -> dport;
            sport = flow_tuple -> sport;
            l4_proto = flow_tuple -> l4_proto;
	    };

	    rev_flow_stat = <map_name>.lookup(&flow_tuple);
	    if(rev_flow_stat) {
	        return 0;
	    }

	    flow_stat = <map_name>.lookup(&flow_tuple); // this prevents transmitted packets from being counted
	    if (flow_stat) {
	        flow_stat->flow_cnt += 1;
	        flow_stat->flow_bytes += pkt_len;
	    } else {
	        struct flow_stat_t tmp_flow_stat = {.flow_cnt = 1, .flow_bytes = pkt_len};
	        <map_name>.update(&flow_tuple, &tmp_flow_stat);
	    }
    }

	DROP:
        return -1;
}

//struct flow_stat_t{
//    u32 start_time;
//    u32 end_time;
//
//    u16 spkt_cnt;
//    u16 dpkt_cnt;
//    u16 spkt_byte;
//    u16 dpkt_byte;
//
//    u16 syn_cnt;
//    u16 ack_cnt;
//    u16 rst_cnt;
//    u16 fin_cnt;
//};