#!/usr/bin/env python3

# Most of these things are adapted from mri_lab_2_se.py; these are where the line numbers come from.

import struct, socket
import numpy as np
import matplotlib.pyplot as plt
import csv
# from PyQt5.QtNetwork import QTcpSocket
import pdb; st = pdb.set_trace
from local_settings import rp_ip_address

from ocra_lib.assembler import Assembler

def read_data():
    # wait for enough data and read to self.buffer
    size = gsocket.bytesAvailable()
    if size <= 0:
        return
    elif self.offset + size < 8 * self.size:
        self.buffer[self.offset:self.offset + size] = gsocket.read(size)
        self.offset += size
        # if the buffer is not complete, return and wait for more
        return
    else:
        self.buffer[self.offset:8 * self.size] = gsocket.read(8 * self.size - self.offset)
        self.offset = 0

    # self.display_data()
    print("Data received!")

def comms_test(s):
    # Assumes a connected socket is supplied
    # gsocket = QTcpSocket()

    # send 2 as signal to start MRI_SE_Widget (L137)
    # gsocket.write(struct.pack('<I', 2))
    s.sendall(struct.pack('<I', 2))

    # setup global socket for receive data (L157)
    # gsocket.readyRead.connect(read_data)

    # send sequence to backend and RP
    ass = Assembler()
    # st()
    seq_byte_array = ass.assemble("sequences/se_default.txt")

    # print(len(seq_byte_array))
    # gsocket.write(struct.pack('<I', len(seq_byte_array)))
    s.sendall(struct.pack('<I', len(seq_byte_array)))
    # gsocket.write(seq_byte_array)
    s.sendall(seq_byte_array)    

    # load shim here

    # Set freq here
    freq = 10 # MHz?
    s.sendall(struct.pack('<I', 1 << 28 | int(1.0e6 * freq)))

    # Set attenuation (has no effect without hardware)
    if False:
        at = 3 # not sure what scale this is in, just a dummy value for now!
        s.sendall(struct.pack('<I', 3 << 28 | int(at/0.25)))    

    # Acquire data
    s.sendall(struct.pack('<I', 2 << 28 | 0 << 24))    
    
    ## receive data
    print("Recv: ")
    # defined by server code? (50000 64-bit complex ints I think; 4
    # acquisitions for spin-echo server-side test
    # bufsize = 5000*8 * 10
    # bufsize = 50000*8 * 10
    bufsize = 100000 * 8
    # bufsize += 8*100 # just an extra 8 bytes for dbg
    buf = bytearray(bufsize)
    recvd = 0
    # recvsz = 1024
    # recvsz = 5000*8
    recvsz = 8
    while(recvd < bufsize):
        rdata = s.recv(recvsz)
        buf[recvd:recvd+recvsz] = rdata
        recvd += recvsz
        # print(recvd//8)

    print("Received {:d} complex64 ints".format(recvd//8))

    data = np.frombuffer(buf, np.complex64)
    
    return data

def display(data):
    approx_sampling_period = 231830 # Hz, approximate for now until we figure out sampling division
    N = data.size
    t_axis = np.linspace(0,(N-1)/approx_sampling_period, N)
    t_axis_us = t_axis*1e6
    if True:
        x = t_axis_us
    else:
        x = np.arange(N)
    plt.plot(x, np.real(data))
    plt.plot(x, np.imag(data))
    plt.xlabel('time (us)')
    plt.show()

    return t_axis_us, data

# if __name__ == "__main__":
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # # gsocket.connectToHost(addr, 1001)
    s.connect((rp_ip_address, 1001))

    data = comms_test(s)
    t, data = display(data)

    if False:
        # just for debugging the CSV saving
        t = np.linspace(0,2*np.pi,10)
        data = np.cos(t) + 1j * np.sin(t)

    data_block = np.vstack([t, data]).T # just create a column matrix of the two vectors
    np.savetxt("data.csv", data_block, delimiter=",")    
