from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QTextBrowser
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
                sniff(iface=self.interface, filter="src port 1500", prn=self.getPacket, count=1)

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
    data = str(pkt[TCP].payload)
    flag = get_flag(pkt)

    textDisplay.append(info)
    textDisplay.append('Data: ' + data)
    textDisplay.append('Flag: ' + flag + '\n')


def receivedThreadFinished():
    textDisplay.append("Sniffer disconnected.\n")
    btnConnect.setText("Connect")


def btnExitClicked(self):
    if snifferWindow.isConnected:
        snifferWindow.disconnect()
    sys.exit(0)


def btnConnectClicked(self):
    if not snifferWindow.isConnected:
        snifferWindow.connect()
        textDisplay.append("Sniffer Connected.\n")
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

    textDisplay = QTextBrowser()
    textDisplay.setStyleSheet("font: 10pt; color: #00cccc; background-color: #001a1a;")

    layoutV = QVBoxLayout(snifferWindow.centralWidget())
    layoutV.addWidget(textDisplay)
    layoutV.addWidget(btnConnect)
    layoutV.addWidget(btnExit)
    snifferWindow.show()

    sys.exit(app.exec_())
