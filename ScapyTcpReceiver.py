import binascii

from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QTextBrowser
from scapy.all import *
from PyQt5 import QtWidgets, QtCore
from scapy.layers.l2 import Ether
from _struct import *

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
    threadFinishedSignal = QtCore.pyqtSignal()

    def __init__(self, interface=iface):
        super().__init__()
        self.interface = interface
        self._lock = threading.Lock()
        self._isRunning = False

    @QtCore.pyqtSlot()
    def run(self):
        self._isRunning = True
        print('received start signal from window.')
        while self._isRunning:
            with self._lock:
                try:
                    sniff(iface=self.interface, filter="src port 1500", prn=self.getPacket, count=1, timeout=2)
                except BaseException as e:
                    logging.error("scapy.sniff error: %s" % e)

    def stop(self):
        self._isRunning = False
        print('received stop signal from window.')
        with self._lock:
            self.threadFinishedSignal.emit()

    def getPacket(self, pkt):
        if self._isRunning:
            self.receivedPacketSignal.emit(pkt)


def receivedPacket(pkt):
    info = str(pkt[0].summary())
    flag = get_flag(pkt)

    packet = pkt.original

    # Extract the 14bytes ethernet header and strip out the DstMAC, SrcMac and ethType
    ether_head = packet[0:14]
    eth_hd = struct.unpack("!6s6s2s", ether_head)  # Split with Big Endian format the 6byte MACs and the 2Byte ethType

    srcMac = str(binascii.hexlify(eth_hd[0]).decode("utf-7"))
    dstMac = str(binascii.hexlify(eth_hd[1]).decode("utf-8"))
    ethType = str(binascii.hexlify(eth_hd[2]).decode("utf-8"))

    # Extract the IP Header Field
    ip_head = packet[14:34]
    ip_head_unpacked = struct.unpack("!1s1s1H1H2s1B1B2s4s4s", ip_head)  # Rip out all the fields in the IP

    ver_head_length = str(binascii.hexlify(ip_head_unpacked[0]).decode("utf-8"))
    service_field = str(binascii.hexlify(ip_head_unpacked[1]).decode("utf-8"))
    total_length = str(ip_head_unpacked[2])
    identification = str(ip_head_unpacked[3])
    flag_frag = str(binascii.hexlify(ip_head_unpacked[4]).decode("utf-8"))
    ttl = str(ip_head_unpacked[5])
    protocol = str(ip_head_unpacked[6])
    checkSum = str(binascii.hexlify(ip_head_unpacked[7]).decode("utf-8"))
    src_ip = str(socket.inet_ntoa(ip_head_unpacked[8]))
    dst_ip = str(socket.inet_ntoa(ip_head_unpacked[9]))

    # Extract the TCP Header
    tcpHeader = packet[34:54]
    tcp_hdr = struct.unpack("!HHII2sH2sH", tcpHeader)

    dst_port = str(tcp_hdr[0])
    src_port = str(tcp_hdr[1])
    seq_no = str(tcp_hdr[2])
    ack_no = str(tcp_hdr[3])
    head_length_6_point = str(binascii.hexlify(tcp_hdr[4]).decode("utf-8"))
    window_size = str(tcp_hdr[5])
    checksum = str(binascii.hexlify(tcp_hdr[6]).decode("utf-8"))
    urgent_pointer = str(tcp_hdr[7])
    data = str(packet[54:].decode("utf-8"))

    listWidget.append('Info\t: ' + info)
    listWidget.append('Source\t: ' + srcMac + ' : ' + src_ip + ' : ' + src_port)
    listWidget.append('Dest\t: ' + dstMac + ' : ' + dst_ip + ' : ' + dst_port)
    listWidget.append('Protocol\t: ' + protocol)
    listWidget.append('Data\t: ' + data)
    listWidget.append('Total length\t: ' + total_length + '\n')

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


def receivedThreadFinished():
    listWidget.append("Sniffer disconnected.\n")
    btnConnect.setText("Connect")


def btnExitClicked(self):
    if snifferWindow.isConnected:
        snifferWindow.disconnect()
    sys.exit(0)


def btnConnectClicked(self):
    if not snifferWindow.isConnected:
        snifferWindow.connect()
        listWidget.append("Sniffer Connected.\n")
        btnConnect.setText("Disconnect")
    else:
        snifferWindow.disconnect()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, _isConnected):
        super().__init__()
        self._isConnected = _isConnected
        self.resize(480, 600)
        self.setWindowTitle("Network Sniffer by Türkay Biliyor")

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        self.worker = SnifferThread()
        self.workerThread = QtCore.QThread()  # Move the Worker object to the Thread object
        self.workerThread.started.connect(self.worker.run)  # Init worker run() at startup (optional)
        self.worker.receivedPacketSignal.connect(receivedPacket)  # Connect your signals/slots
        self.worker.threadFinishedSignal.connect(receivedThreadFinished)  # Connect your signals/slots
        self.worker.moveToThread(self.workerThread)
        self.workerThread.setTerminationEnabled(True)

    def connect(self):
        self.workerThread.start()
        self.isConnected = True

    def disconnect(self):
        self.worker.stop()
        self.workerThread.quit()
        self.workerThread.wait()
        self.isConnected = False

    def __del__(self):
        self.workerThread.quit()
        self.workerThread.wait()

    @property
    def isConnected(self):
        return self._isConnected

    @isConnected.setter
    def isConnected(self, value):
        self._isConnected = value


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    snifferWindow = MainWindow(False)

    btnConnect = QPushButton("Connect")
    btnConnect.clicked.connect(btnConnectClicked)

    btnExit = QPushButton("Exit")
    btnExit.clicked.connect(btnExitClicked)

    listWidget = QTextBrowser()
    listWidget.setStyleSheet("font: 10pt; color: #00cccc; background-color: #001a1a;")

    layoutV = QVBoxLayout(snifferWindow.centralWidget())
    layoutV.addWidget(listWidget)
    layoutV.addWidget(btnConnect)
    layoutV.addWidget(btnExit)
    snifferWindow.show()

    sys.exit(app.exec_())
