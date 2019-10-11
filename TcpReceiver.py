import binascii
import socket
import struct
import sys

BUFFER_SIZE = 1024
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 10000)
sock.bind(server_address)
sock.listen(1)

while True:
    print('waiting for a connection')
    connection, client_address = sock.accept()

    try:
        # Receive the data in small chunks and retransmit it
        while True:
            pkt = connection.recv(BUFFER_SIZE)
            packet = pkt[0:14]
            ether_head = packet[0:14]
            eth_hd = struct.unpack("!6s6s2s",
                                   ether_head)  # Split with Big Endian format the 6byte MACs and the 2Byte ethType

            srcMac = str(binascii.hexlify(eth_hd[0]).decode("utf-7"))
            dstMac = str(binascii.hexlify(eth_hd[1]).decode("utf-8"))
            ethType = str(binascii.hexlify(eth_hd[2]).decode("utf-8"))

            # Extract the IP Header Field
            ip_head = pkt[14:34]
            ip_head_unpacked = struct.unpack("!1s1s1H1H2s1B1B2s4s4s", ip_head)  # Rip out all the fields in the IP

            ver_head_length = binascii.hexlify(ip_head_unpacked[0]).decode()
            service_field = binascii.hexlify(ip_head_unpacked[1]).decode()
            total_length = str(ip_head_unpacked[2])
            identification = str(ip_head_unpacked[3])
            flag_frag = binascii.hexlify(ip_head_unpacked[4]).decode()
            ttl = str(ip_head_unpacked[5])
            protocol = str(ip_head_unpacked[6])
            checkSum = binascii.hexlify(ip_head_unpacked[7]).decode()
            src_ip = socket.inet_ntoa(ip_head_unpacked[8])
            dst_ip = socket.inet_ntoa(ip_head_unpacked[9])

            # Extract the TCP Header
            tcpHeader = pkt[34:54]
            tcp_hdr = struct.unpack("!HHII2sH2sH", tcpHeader)

            dst_port = str(tcp_hdr[0])
            src_port = str(tcp_hdr[1])
            seq_no = str(tcp_hdr[2])
            ack_no = str(tcp_hdr[3])
            head_length_6_point = binascii.hexlify(tcp_hdr[4]).decode()
            window_size = str(tcp_hdr[5])
            checksum = binascii.hexlify(tcp_hdr[6]).decode()
            urgent_pointer = str(tcp_hdr[7])
            data = str(pkt[54:].decode())

            print("\nEthernet Header")
            print("Source MAC: ", srcMac)
            print("Destination MAC: ", dstMac)
            print("Ethernet Type: ", ethType)

            print("\nIP Header")
            print("Version and head length: ", ver_head_length)
            print("Service Field: ", service_field)
            print("Total length: ", total_length)
            print("Identification: ", identification)
            print("Flag and fragment offset: ", flag_frag)
            print("Time to live: ", ttl)
            print("Protocol: ", protocol)
            print("Checksum: ", checkSum)
            print("Source IP: ", src_ip)
            print("Destination IP: ", dst_ip)

            print("\nTCP Header")
            print("Source Port Number: ", src_port)
            print("Destination Port Number: ", dst_port)
            print("Sequence Number: ", seq_no)
            print("Acknowledgment Number: ", ack_no)
            print("Header Length Reserved and Six Pointers: ", head_length_6_point)
            print("Window size: ", window_size)
            print("Checksum: ", checksum)
            print("Urgent Pointer: ", urgent_pointer)
            print("Data: ", data)

    finally:
        # Clean up the connection
        connection.close()
