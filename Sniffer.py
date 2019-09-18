from scapy.all import *
from PyQt5 import QtWidgets, QtCore
from scapy.layers.inet import TCP
from scapy.layers.l2 import Ether

iface = "Ethernet"

FIN = 0x01
SYN = 0x02
RST = 0x04
PSH = 0x08
ACK = 0x10
URG = 0x20
ECE = 0x40
CWR = 0x80


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


"""
#non qt version
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


def startSniffer():
    sniffer = Sniffer()
    print("Start sniffing...")
    sniffer.start()
    sniffer.join()
    
def main():
startSniffer()

"""


# qt version
class SnifferThread(QtCore.QObject):
    receivedPacketSignal = QtCore.pyqtSignal(Ether)

    def __init__(self, interface=iface):
        super().__init__()
        self.interface = interface

    @QtCore.pyqtSlot()
    def run(self):
        sniff(iface=self.interface, filter="src port 1500", prn=self.getPacket)

    def getPacket(self, pkt):
        self.receivedPacketSignal.emit(pkt)


def receivedPacket(pkt):
    print(pkt[0].summary())
    pkt[TCP].payload = str(pkt[TCP].payload)
    print('Data: ' + str(pkt[TCP].payload))
    print('Flag: ' + get_flag(pkt))


class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        print("Starting sniffing...")
        self.worker = SnifferThread()
        self.workerThread = QtCore.QThread()  # Move the Worker object to the Thread object
        self.workerThread.started.connect(self.worker.run)  # Init worker run() at startup (optional)
        self.worker.receivedPacketSignal.connect(receivedPacket)  # Connect your signals/slots
        self.worker.moveToThread(self.workerThread)
        self.workerThread.start()

    def __del__(self):
        print("Stopping sniffing...")
        self.workerThread.quit();
        self.workerThread.wait();


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    sniffer = Main()
    sys.exit(app.exec_())
