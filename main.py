import random
import tkinter as tk
from tkinter import ttk
from client.clientGui import start_client_gui
import tcp_creator
from logger import setup_logger


def server():
    print('server')
    main_interface.destroy()


def client():
    main_interface.destroy()
    start_client_gui()


# window
main_interface = tk.Tk()
main_interface.title('SSL Network')
main_interface.geometry('500x250')

# frames

# buttons
__button_style = ttk.Style()
__button_style.theme_use('alt')
__button_style.configure('TButton', background='white', font=('Arial', 12, 'bold'))
ttk.Button(main_interface, style='TButton', text='Server', command=server).grid(row=0, column=0, sticky='nsew')
ttk.Button(main_interface, style='TButton', text='Client', command=client).grid(row=0, column=1, sticky='nsew')

# run
# setup_logger()
main_interface.grid_columnconfigure(0, weight=1)
main_interface.grid_columnconfigure(1, weight=1)
main_interface.grid_rowconfigure(0, weight=1)
main_interface.mainloop()
