from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP

iface = "Ethernet"
# VARIABLES
src = "127.0.0.1"
dst = "127.0.0.1"
sport = int(1500)
dport = int(3500)


def send_packet(protocol=None, src_ip=None, src_port=None, flags=None, dst_ip=None, dst_port=None, iface=None,
                message=None):
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
        send_packet("tcp", src, sport, 'S', dst, dport, iface,
                    "Send by Turkay : " + datetime.now().strftime("%m/%y %H:%M:%S"))
        time.sleep(1)


if __name__ == "__main__":
    main()
