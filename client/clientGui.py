import socket
import time
import tkinter as tk
from tkinter import ttk
from client.clientApp import ClientApp
from client.utilities import get_protocol


def start_client_gui():
    client_window = tk.Tk()
    client = ClientApp()
    while True:
        # host = ('cloudflare.com', 443)  # TODO Enter host address
        # host = ('162.19.227.101', 8080)
        host = ('google.pl', 80)
        # host = ('xapi.xtb.com', 5124)
        protocol = get_protocol(host)
        if protocol != socket.AF_UNSPEC:
            if client.connect(host, protocol):
                print("Client Connected")
                break

    ttk.Label(client_window, textvariable=client.state_).pack()
    ttk.Button(client_window, command=client.check_threads_state, text='Check threads').pack()
    # ttk.Button(client_window, command=client.do_the_handshake, text='Do the handshake').pack()
    ttk.Button(client_window, command=client.keep_alive, text='Keep alive').pack()
    ttk.Button(client_window, command=client.test, text='test').pack()
    client_window.mainloop()
