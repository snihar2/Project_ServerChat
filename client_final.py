import socket
import sys
import threading
import struct
import pickle
from datetime import datetime


IpAdress = input('IpServerAdress :\n')
Port = int(input('PortServerAdress :\n'))  # 6000
SERVERADDRESS = (IpAdress, Port)


class Chat:
    def __init__(self):
        self.__pseudo = input("Welcome to the chat, please enter your nickname :\n")
        self.__ip = None
        self.__port = None
        self.__clients_list = {}

    def run(self):
        self.__running = True
        self.__address = None

        # Command for the client
        handlers = {
            '/exit': self._exit,
            '/quit': self._quit,
            '/join': self._join,
            '/send': self._send,
            '/clients': self._who_s_on,
            '/connect': self._pseudo_to_server
        }
        for i in handlers.keys():
            print(i)
        print("Enter command !")

        while self.__running:
            line = sys.stdin.readline().rstrip() + ' '
            # Extract the command and the param
            command = line[:line.index(' ')]
            param = line[line.index(' ') + 1:].rstrip()
            # Call the command handler
            if command in handlers:
                try:
                    handlers[command]() if param == '' else handlers[command](param)
                except:
                    print("Error with the execution of the command")
            else:
                print('Unknown command:', command)

    def _chat(self):
        s = socket.socket(type=socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.bind((socket.gethostname(), int(self.__port)))
        self.__s = s
        print('Listen on {}:{}'.format(socket.gethostname(), int(self.__port)))
        threading.Thread(target=self._receive).start()

    def _exit(self):
        # function to exit the application
        self._server_connection("disconnect")
        print("Application closed")
        self.__running = False
        self.__address = None
        self.__s.close()
        self.__t.close()

    def _quit(self):
        # function to disconnect from an user
        try:
            print("Disconnected from " + str(self.__address[0]))
            self.__address = None
        except TypeError:
            print("You're not connected to anyone")

    def _join(self, param):
        # function to make connection with another user to chat
        tokens = self.__clients_list[param]
        try:
            self.__address = (param, (tokens['ip'], int(tokens['port'])))
            print('Connected to {}:{}'.format(*self.__address))
        except OSError:
            print("Error while trying to connect")

    def _send(self, param):
        # function which makes sending a message possible and gives a structure to this message when sent
        if self.__address is not None:
            try:
                print("To " + "[" + self.__address[0] + "]" + ": "+param)
                message = (self.__pseudo + " " + param).encode()
                total_sent = 0
                while total_sent < len(message):
                    sent = self.__s.sendto(message[total_sent:], self.__address[1])
                    total_sent += sent
            except OSError:
                print('Error while sending the message')

    def _receive(self):
        # function which makes receiving a message possible and gives a structure to this message
        if self.__s is not None:
            while self.__running:
                try:
                    data, address = self.__s.recvfrom(1024)
                    msg = data.decode()
                    pseudo = msg.split(" ")[0]
                    message = msg.split(" ")[1]
                    print(datetime.now().strftime('%H:%M:%S') + " [" + pseudo + "]" + ": " + message)
                    if pseudo not in self.__clients_list:
                        print("Type \"/join " + pseudo + "\" to start chatting with " + pseudo)
                        self._clients()

                except socket.timeout:
                    pass
                except OSError:
                    return

    def _clients(self):
        # function which stores the users connected on the server
        clients = self._server_connection("clients")
        list_of_clients = {}
        for i in clients.split("\n")[:-1]:
            data = i.split(" ")
            name = data[0]
            ip = data[1]
            port = data[2]
            coords = {"ip": None, "port": None}
            coords["ip"] = ip
            coords["port"] = port
            list_of_clients[name] = coords
        self.__clients_list = list_of_clients
        return self.__clients_list

    def _who_s_on(self):
        # function called by /clients which displays the users on the server
        self._clients()
        print("Clients connected on the server :")
        for i in self.__clients_list.keys():
            print(i)

    def _pseudo_to_server(self):
        pseudo_port = (self._server_connection(self.__pseudo)).split(" ")
        print(pseudo_port)
        self.__pseudo = pseudo_port[0]
        self.__ip = pseudo_port[1]
        self.__port = pseudo_port[2]
        self.__clients_list[pseudo_port[0]] = {"ip": self.__ip, "port": self.__port}
        self._chat()

    def _server_connection(self, message):
        # function which connects the user to the server
        self.__t = socket.socket()
        self.__t.connect(SERVERADDRESS)
        try:
            total_sent = 0
            msg = pickle.dumps(message.encode())
            self.__t.send(struct.pack('I', len(msg)))
            while total_sent < len(msg):
                sent = self.__t.send(msg[total_sent:])
                total_sent += sent
            data = self.__t.recv(1024).decode()
            return data
        except OSError:
            print("Communication error with the server")


if __name__ == '__main__':
        Chat().run()