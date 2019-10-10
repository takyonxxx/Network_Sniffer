import binascii
import socket
import struct

if __name__ == '__main__':
    # Create Raw Socket
    TCP_IP = '127.0.0.1'
    TCP_PORT = 3500
    BUFFER_SIZE = 2048

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        s.connect((TCP_IP, TCP_PORT))
    except Exception as e:
        print("Exception: %s" % (e))

    while True:
        pkt = s.recvfrom(BUFFER_SIZE)
        # Extract the 14bytes ethernet header and strip out the DstMAC, SrcMac and ethType
        ether_head = pkt[0][0:14]
        eth_hd = struct.unpack("!6s6s2s", ether_head)  # Split with Big Endian format the 6byte MACs and the 2Byte ethType

        srcMac = binascii.hexlify(eth_hd[0])
        dstMac = binascii.hexlify(eth_hd[1])
        ethType = binascii.hexlify(eth_hd[2])

        # Extract the IP Header Field
        ip_head = pkt[0][14:34]
        ip_head_unpacked = struct.unpack("!1s1s1H1H2s1B1B2s4s4s", ip_head)  # Rip out all the fields in the IP

        ver_head_length = binascii.hexlify(ip_head_unpacked[0])
        service_field = binascii.hexlify(ip_head_unpacked[1])
        total_length = str(ip_head_unpacked[2])
        identification = str(ip_head_unpacked[3])
        flag_frag = binascii.hexlify(ip_head_unpacked[4])
        ttl = str(ip_head_unpacked[5])
        protocol = str(ip_head_unpacked[6])
        checkSum = binascii.hexlify(ip_head_unpacked[7])
        src_ip = socket.inet_ntoa(ip_head_unpacked[8])
        dst_ip = socket.inet_ntoa(ip_head_unpacked[9])

        # Extract the TCP Header
        tcpHeader = pkt[0][34:54]
        tcp_hdr = struct.unpack("!HHII2sH2sH", tcpHeader)

        dst_port = str(tcp_hdr[0])
        src_port = str(tcp_hdr[1])
        seq_no = str(tcp_hdr[2])
        ack_no = str(tcp_hdr[3])
        head_length_6_point = binascii.hexlify(tcp_hdr[4])
        window_size = str(tcp_hdr[5])
        checksum = binascii.hexlify(tcp_hdr[6])
        urgent_pointer = str(tcp_hdr[7])
        data = pkt[0][54:]

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
