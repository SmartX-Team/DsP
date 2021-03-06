#!/usr/bin/python
#
# xdp_drop_count.py Drop incoming packets on XDP layer and count for which
#                   protocol type
#
# Copyright (c) 2016 PLUMgrid
# Copyright (c) 2016 Jan Ruth
# Licensed under the Apache License, Version 2.0 (the "License")
from bcc import BPF
import pyroute2
import time
import sys
from ctypes import *
from kafka import KafkaConsumer
import os
import subprocess

bootstrap_servers = ['210.117.251.25'] # k-post
topicName = 'bpf2'

consumer = KafkaConsumer(topicName, bootstrap_servers = bootstrap_servers)

entire_bpf_map_info = str(subprocess.check_output(["bpftool","map","show",]))

def update_bpf_map(val1, val2, val3, val4):
    print("-add input value: " + str(val1) + ' ' + str(val2) + ' ' + str(val3) + ' ' + str(val4))
    subprocess.call(["bpftool","map","update","id",str(black_list_map_id),"key",str(val1),str(val2),str(val3),str(val4),"value","01"])
#    print("bpf map with id " + str(black_list_map_id) + "updated...")
#    subprocess.call(["bpftool","map","lookup","id",str(black_list_map_id),"key",])

def delete_bpf_map(val1, val2, val3, val4):
    print('-del input value: ' + str(val1) + ' ' + str(val2) + ' ' + str(val3) + ' ' + str(val4))
    subprocess.call(['bpftool','map','delete','id',str(black_list_map_id),'key',str(val1),str(val2),str(val3),str(val4)])

def kafka_consumer():
    print('kafka consumer initiated....')
    try:
        for message in consumer:
            print(message.value)
    except KeybaordInterrupt:
            sys.exit()

def convert_ip_to_bin(data):
        data =  "{0:b}".format(data.value).zfill(28)
        #    data = ''.join(str((int((data[0:4]),2))))
        # 0:4 - 1
        # 4:12 - 1
        # 12:20 - 168
        # 20:28

        one = ''.join(str((int((data[20:28]),2))))
        two = ''.join(str((int((data[12:20]),2))))
        three = ''.join(str((int((data[4:12]),2))))
        four = ''.join(str((int((data[0:4]),2))))
        back = one +'.' + two + '.'+ three +'.' + four
        return back

flags = 0
def usage():
    print("Usage: {0} [-S] <ifdev>".format(sys.argv[0]))
    print("       -S: use skb mode\n")
    print("       -H: use hardware offload mode\n")
    print("e.g.: {0} eth0\n".format(sys.argv[0]))
    exit(1)

if len(sys.argv) < 2 or len(sys.argv) > 3:
    usage()

offload_device = None
if len(sys.argv) == 2:
    device = sys.argv[1]
elif len(sys.argv) == 3:
    device = sys.argv[2]

_xdp_file = "../hash_map_xdp_drop.c"

maptype = "percpu_array"
if len(sys.argv) == 3:
    if "-S" in sys.argv:
        # XDP_FLAGS_SKB_MODE
        flags |= (1 << 1)
    if "-H" in sys.argv:
        # XDP_FLAGS_HW_MODE
        maptype = "array"
        offload_device = device
        flags |= (1 << 3)

mode = BPF.XDP
#mode = BPF.SCHED_CLS

if mode == BPF.XDP:
    ret = "XDP_PASS"
    ctxtype = "xdp_md"
else:
    ret = "TC_ACT_SHOT"
    ctxtype = "__sk_buff"

# load BPF program
b = BPF(src_file = _xdp_file, cflags=["-w", "-DRETURNCODE=%s" % ret, "-DCTXTYPE=%s" % ctxtype, "-DMAPTYPE=\"%s\"" % maptype], )

fn = b.load_func("xdp_prog1", mode)

if mode == BPF.XDP:
    b.attach_xdp(device, fn, flags)
else:
    ip = pyroute2.IPRoute()
    ipdb = pyroute2.IPDB(nl=ip)
    idx = ipdb.interfaces[device].index
    ip.tc("add", "clsact", idx)
    ip.tc("add-filter", "bpf", idx, ":1", fd=fn.fd, name=fn.name,
          parent="ffff:fff2", classid=1, direct_action=True)

hash_addr = b.get_table("black_list")

prev = [0] * 256
print("Printing drops per IP protocol-number, hit CTRL+C to stop")
#ip_addr = str(convert_ip_to_bin((hash_addr.items()[0][1])))

# remove the annotation block and integratre this code later
# save black_list map id - begin
num = entire_bpf_map_info.find("black_list")
test = num - 30
test2 = entire_bpf_map_info[test:num]
num2 = test2.find('\n')
test3 = test2[num2:]
num3 = test3.find(':')
test4 = test3[:num3]
black_list_map_id = int(test4)
print('- targetted bpf map id : ' + str(test4))
#save black_list map id - end

while 1:
    print('filtering...')
    time.sleep(10)
    #under while
#    try:
        # here
#        time.sleep(1)
#    except KeyboardInterrupt:
#        print("Removing filter from device")
#        break;

if mode == BPF.XDP:
    b.remove_xdp(device, flags)
else:
    ip.tc("del", "clsact", idx)
    ipdb.release()
