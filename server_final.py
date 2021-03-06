import socket
import struct
import pickle
import sys


SERVERADDRESS = ('0.0.0.0', 6000)


class Server:
    def __init__(self):
        self.__s = socket.socket()
        self.__s.bind(SERVERADDRESS)
        self.__clients = {}

    def run(self):
        self.__s.listen()
        while True:
            client, addr = self.__s.accept()
            print(client, addr)
            clt = self._receive(client)
            try:
                if clt == 'clients':
                    self._handle(client)

                elif clt == 'port':
                    client.send(str(addr[1]).encode())

                elif clt == 'disconnect':
                    for i, j in self.__clients.items():
                        if j[0] == addr[0]:
                            del self.__clients[i]
                else:
                    self.__clients[clt] = addr
                    client.send(("{} {} {}".format(clt, addr[0], addr[1])).encode())
                client.close()
            except OSError:
                print('Error with the reception of message')

    def _receive(self, client):
        size = struct.unpack('I', client.recv(4))[0]
        data = pickle.loads(client.recv(size)).decode()
        return data

    def _handle(self, client):
        clt = ""
        for i, j in self.__clients.items():
            clt += ("{} {} {}\n".format(i, j[0], j[1]))
        print(clt)
        client.send(clt.encode())


if __name__ == '__main__':
        Server().run()
