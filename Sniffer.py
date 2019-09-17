from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP
from threading import Thread

iface = "Ethernet"

FIN = 0x01
SYN = 0x02
RST = 0x04
PSH = 0x08
ACK = 0x10
URG = 0x20
ECE = 0x40
CWR = 0x80


class Sniffer(Thread):
    def __init__(self, interface=iface):
        super().__init__()

        self.interface = interface

    def run(self):
        sniff(iface=self.interface, filter="src port 1500", prn=self.print_packet)

    def print_packet(self, pkt):
        print(pkt[0].summary())
        pkt[TCP].payload = str(pkt[TCP].payload)
        print('Data: ' + str(pkt[TCP].payload))
        print('Flag: ' + get_flag(pkt))


def get_flag(pkt):

    F = pkt['TCP'].flags  # this should give you an integer
    if F & FIN:
        return "FIN - Finish"
    if F & SYN:
        return "SYN - Synchronization"
    if F & RST:
        return "RST - Reset"
    if F & PSH:
        return "PSH - Push"
    if F & ACK:
        return "ACK - Acknowledgement"
    if F & URG:
        return "URG - Urgent"
    if F & ECE:
        return "ECE -  ECN capable"
    if F & CWR:
        return "CWR - Congestion Window Reduced"

    return "NS - Nonce Sum"


def startSniffer():
    sniffer = Sniffer()
    print("[*] Start sniffing...")
    sniffer.start()


def main():
    startSniffer()


if __name__ == "__main__":
    main()
