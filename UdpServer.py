import socket


def listener(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = ('127.0.0.1', int(port))
    print('Listening on {} {}'.format(server_addr[0], server_addr[1]))
    sock.bind(server_addr)
    while True:
        data, addr = sock.recvfrom(1024)
        print(data)


if __name__ == '__main__':
        listener(8080)
