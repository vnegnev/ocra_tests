#!/usr/bin/env python3

# Most of these things are adapted from mri_lab_2_se.py; these are where the line numbers come from.

from PyQt5.QtNetwork import QTcpSocket

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

def comms_test():
    gsocket = QTcpSocket()

    addr = "192.168.1.2"
    gsocket.connectToHost(addr, 1001)    

    # send 2 as signal to start MRI_SE_Widget (L137)
    gsocket.write(struct.pack('<I', 2))    

    # setup global socket for receive data (L157)
    gsocket.readyRead.connect(read_data)

    # send sequence to backend and RP
    ass = Assembler()
    seq_byte_array = ass.assemble("sequences/se_default.txt")
    print(len(seq_byte_array))
    gsocket.write(struct.pack('<I', len(seq_byte_array)))
    gsocket.write(seq_byte_array)    

    # load shim here
