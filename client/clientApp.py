import socket
import random
import threading
from tkinter import StringVar
import client.utilities as uti
import tcp_creator


class ClientApp:
    state_: StringVar
    id_: bytes
    sequence_number: int
    client: socket.socket
    class_threads: list
    host_protocol: str
    __event_thread: threading.Thread
    __recv_thread: threading.Thread

    def __init__(self):
        self.state_  = StringVar()
        self.host_protocol = 'Unknown'
        self.__event_thread = threading.Thread(target=self.event_manager)
        self.__recv_thread = threading.Thread(target=self.read)
        self.class_threads = [self.__event_thread, self.__recv_thread]
        return

    def __set_protocol(func):
        def setter(self):
            self.host_protocol = func(self)
        return setter

    def __on_connect(func):
        def start_tasks(self, server, family) -> bool:
            state = func(self, server, family)
            if state:
                # self.get_server_protocol()
                self.state_.set('CONNECTED')
                self.sequence_number = 0
                # self.event_thread.start()
                self.__recv_thread.start()
            return state
        return start_tasks

    @__on_connect
    def connect(self, server: tuple, family: socket.AddressFamily) -> bool:
        """server: tuple (ip, port)"""
        self.client = socket.socket(family, socket.SOCK_RAW, socket.IPPROTO_RAW)
        self.client.settimeout(5)

        try:
            self.client.connect(server)
            return True
        except socket.herror as e:
            print('[Error] Host error: ' + str(e))
        except socket.timeout:
            print('[Error] Timed out!')
        except socket.error as e:
            print(f'[Error] Socket error: {e}')
        return False
        # socket.AF_INET  - IPv4
        # socket.AF_INET6 - IPv6

    def disconnect(self) -> None:
        if not self.is_connected():
            print('[Error] Client is already disconnected')
            return
        print('[Info] Disconnecting')
        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()
        self.__close_alive_threads()

    @__set_protocol
    def get_server_protocol(self) -> str: # TODO kinda need to remake this one
        send_socket = self.client.dup()
        send_socket.sendall(b"GET / HTTP/1.1\r\nHost: " + self.client.getsockname()[0].encode('utf-8') + b"\r\n\r\n")
        response = send_socket.recv(1024)
        print(response)
        if b"HTTP" in response:
            return 'HTTP'
        if b"TLS" in response:
            return 'TLS'
        return 'Unknown'

    def send(self, data, socket_=None, flags=None) -> bool:
        if socket_ is None:
            socket_ = self.client

        print(f'[Info] Sending {data} with len {len(data)}')
        try:
            sent_size = socket_.send(data, flags) if (flags is not None) else socket_.send(data)
            self.sequence_number += 1
        except socket.error as error:
            print(f'[Error] There was na error {error} while sending message')
            return False

        if sent_size == 0 and sent_size != len(data):
            print('[Error] Connection has been broken')
            self.state_.set('DISCONNECTED')
            return False

        if sent_size < len(data):
            return self.send(data[sent_size:], socket_)
        print('[Debug] Successfully sent message')
        return True

    def read(self) -> None:
        while True:
            try:
                read_ = self.client.recv(65535)
                print(read_)
                print(read_.decode('utf-8'))

                if len(read_) == 0:
                    print('[Error] Connection has been broken')
                    self.state_.set('DISCONNECTED')
                    print(not self.is_connected())

                if not self.is_connected():
                    print("[Info] Closing recv thread")
                    return
            except Exception:
                continue

    def keep_alive(self) -> None:
        print('[Debug] Keep alive')
        state = self.client.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, not state)
        print(f'[Info] Keep alive is now {"enable" if not state else "disable"}')

    def test(self):
        # self.id_ = int(random.Random().random() * 128).to_bytes(1, "big") * 2
        self.id_ = b'\x00\x00'
        self.sequence_number += 1
        message = tcp_creator.create_tcpip_message(self.client, self.id_, self.sequence_number, [tcp_creator.FLAG_SYN, tcp_creator.FLAG_ACK], '')
        print(message)
        self.client.sendto(message, (self.client.getpeername()[0], 0))
    # def do_the_handshake(self):
    #     self.client.send(uti.record)
        
    def is_connected(self) -> bool:
        return True if self.state_.get() == 'CONNECTED' else False

    def event_manager(self) -> None: # TODO funkcja nie potrzebna - to robi recv
        raise NotImplementedError

    def check_threads_state(self) -> None:
        for thread_ in self.class_threads:
            print(f'{thread_.name} is {"Alive" if thread_.is_alive() else "Off"}')

    def __close_alive_threads(self):
        for thread_ in self.class_threads:
            if thread_.is_alive():
                thread_.join()

    def __del__(self):
        print('[Info] Closing client')
        self.__close_alive_threads()
        self.client.close()




