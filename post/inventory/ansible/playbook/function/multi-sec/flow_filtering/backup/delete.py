from bcc import BPF
from kafka import KafkaProducer
from kafka.errors import KafkaError
import time

# Connect kafka producer here

producer = KafkaProducer(bootstrap_servers=['localhost:9093'])
topicName = 'controller'

from ctypes import *
import ctypes as ct
import sys
import socket
import os
import struct

print("=========================packet monitor=============================\n")

kafka_content = 'qqqq'
counter = 0
while 1:
    counter = counter + 1
    producer.send(topicName,kafka_content)
    if (counter == 100):
        break
producer.send(topicName,kafka_content)
