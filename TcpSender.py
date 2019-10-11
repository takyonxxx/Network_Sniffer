#!/usr/bin/python
import binascii
import socket
import struct
import time
from datetime import datetime
from struct import pack

import netifaces

iface = "Ethernet"


def checksum(msg):
    cs = 0

    # loop taking 2 characters at a time
    for i in range(0, len(msg) - 1, 2):
        w = msg[i] + (msg[i + 1] << 8)
        cs = cs + w

    cs = (cs >> 16) + (cs & 0xffff)
    cs = cs + (cs >> 16)

    # complement and mask to 4 byte short
    cs = ~cs & 0xffff

    return cs


def formatMAC(mac):
    return mac.lower().replace(':', '')


def construct_ethernet_header(eth_src, eth_dst, eth_prt):
    e_src = formatMAC(eth_src)
    e_dst = formatMAC(eth_dst)
    e_prt = eth_prt

    eth_pack = struct.pack("!6s6s2s", binascii.unhexlify(e_dst), binascii.unhexlify(e_src), binascii.unhexlify(e_prt))
    return eth_pack


def construct_ip_header(source_ip, dest_ip, ihl=5, ver=4, pid=0, offs=0, ttl=255, proto=socket.IPPROTO_TCP):
    ip_ihl = ihl
    ip_ver = ver
    ip_tos = 0
    ip_tot_len = 0  # kernel will fill the correct total length
    ip_id = pid  # Id of this packet
    ip_frag_off = offs
    ip_ttl = ttl
    ip_proto = proto
    ip_check = 0  # kernel will fill the correct checksum
    ip_saddr = socket.inet_aton(source_ip)
    ip_daddr = socket.inet_aton(dest_ip)

    ip_ihl_ver = (ip_ver << 4) + ip_ihl

    # the ! in the pack format string means network order
    ip_header = struct.pack('!BBHHHBBH4s4s', ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto,
                            ip_check, ip_saddr, ip_daddr)
    return ip_header


def construct_tcp_header(source_ip, dest_ip, srcp, dstp, seq, ackno, flags, user_data="", doff=5, wsize=5840, urgptr=0):
    tcp_source = srcp  # source port
    tcp_dest = dstp  # destination port
    tcp_seq = seq
    tcp_ack_seq = ackno
    tcp_doff = doff
    # tcp flags
    # flags=[HS,CWR,ECE,URG,ACK,PSH,RST,SYN,FIN]
    tcp_fin = flags[8]
    tcp_syn = flags[7]
    tcp_rst = flags[6]
    tcp_psh = flags[5]
    tcp_ack = flags[4]
    tcp_urg = flags[3]
    tcp_window = socket.htons(5840)  # maximum allowed window size
    tcp_check = 0
    tcp_urg_ptr = urgptr

    tcp_offset_res = (tcp_doff << 4) + 0
    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)

    # the ! in the pack format string means network order
    tcp_header = struct.pack('!HHLLBBHHH', tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,
                             tcp_window, tcp_check, tcp_urg_ptr)

    # pseudo header fields
    source_address = socket.inet_aton(source_ip)
    dest_address = socket.inet_aton(dest_ip)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header) + len(user_data)

    psh = struct.pack('!4s4sBBH', source_address, dest_address, placeholder, protocol, tcp_length)
    psh = psh + tcp_header + user_data.encode()

    tcp_check = checksum(psh)

    # make the tcp header again and fill the correct checksum
    tcp_header = struct.pack('!HHLLBBH', tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,
                             tcp_window) + struct.pack('H', tcp_check) + struct.pack('!H', tcp_urg_ptr)
    return tcp_header


def construct_tcp_packet(eth_header, ip_header, tcp_header, user_data=""):
    packet = ''
    packet = eth_header + ip_header + tcp_header + user_data.encode()
    return packet


if __name__ == '__main__':

    # Create Raw Socket
    TCP_IP = '127.0.0.1'
    TCP_PORT = 10000
    BUFFER_SIZE = 1024

    srcip = TCP_IP
    destip = TCP_IP
    srcport = TCP_PORT
    destport = TCP_PORT

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (TCP_IP, TCP_PORT)
        s.connect(server_address)
    except Exception as e:
        print("Exception: %s" % (e))

    message = "Send by Turkay Biliyor : " + datetime.now().strftime("%m/%y %H:%M:%S")

    interface = "{4DD3818B-3014-43B4-A128-479203C716F3}"
    networkdetails = netifaces.ifaddresses(interface)
    ipaddress = networkdetails[2][0]['addr']
    macaddress = networkdetails[-1000][0]['addr']

    ethhead = construct_ethernet_header(macaddress, macaddress, "0800")
    iphead = construct_ip_header(srcip, destip)
    tcphead = construct_tcp_header(srcip, destip, srcport, destport, 1, 0, [0, 0, 0, 0, 0, 0, 0, 1, 0])
    tcppacket = construct_tcp_packet(ethhead, iphead, tcphead, message)

    while True:
        s.sendall(tcppacket)
        time.sleep(1)
