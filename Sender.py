from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP

iface = "Ethernet"
# VARIABLES
src = "127.0.0.1"
dst = "127.0.0.1"
sport = int(1500)
dport = int(3500)
test_content = """HTTP/1.1 200 OK\r\nDate: Wed, 22 Nov 2017 02:13:40 GMT\r\nServer: Apache/2.2.22 (Ubuntu)\r\nLast-Modified: Tue, 21 Nov 2017 04:35:07 GMT\r\nAccept-Ranges: bytes\r\nContent-Length: 177\r\nKeep-Alive: timeout=500, max=100\r\nConnection: Keep-Alive\r\nContent-Type: text/html\r\n\r\n<html><body><h1>It !!!!!!</h1>
<p>This is the default web page for this server.!!!!!</p>
<p>The web server software is running but no content has been added, yet.</p>
</body></html>""" + datetime.now().strftime("%m/%y %H:%M:%S")

def send_packet(protocol=None, src_ip=None, src_port=None, flags=None, dst_ip=None, dst_port=None, iface=None, message=None ):
    """Modify and send an IP packet."""
    if protocol == 'tcp':
        packet = IP(src=src_ip, dst=dst_ip) / TCP(flags=flags, sport=src_port, dport=dst_port) / message
    elif protocol == 'udp':
        if flags: raise Exception(" Flags are not supported for udp")
        packet = IP(src=src_ip, dst=dst_ip) / UDP(sport=src_port, dport=dst_port) / message
    else:
        raise Exception("Unknown protocol %s" % protocol)

    send(packet, iface=iface)


def main():
    while True:
        send_packet("tcp", src, sport, 'S', dst, dport, iface, "Send by Turkay : " + datetime.now().strftime("%m/%y %H:%M:%S"))
        time.sleep(1)


if __name__ == "__main__":
    main()
