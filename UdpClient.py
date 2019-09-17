
import socket
import time
from datetime import datetime


def icmp():
    icmp_pkt = "Send by Turkay : " + datetime.now().strftime("%m/%y %H:%M:%S")
    return icmp_pkt.encode()


# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# define a server socket information
ip = ('127.0.0.1', 8080)
# and connetctions this socket
s.connect((ip))

while True:
    # sending custom package to server socket every half a second
    time.sleep(1)
    s.send(icmp())
