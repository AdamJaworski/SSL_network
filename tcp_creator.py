import binascii
import socket
import random
from ast import literal_eval

FLAG_FIN = '000000001'
FLAG_SYN = '000000010'
FLAG_RST = '000000100'
FLAG_PSH = '000001000'
FLAG_ACK = '000010000'
FLAG_URG = '000100000'


def add_bin(no1: str, no2: str) -> str:
    if len(no1) != len(no2):
        raise ValueError

    output = ''
    for i in range(len(no2)):
        if no1[i] == '1' or no2[i] == '1':
            output += '1'
        else:
            output += '0'
    return output


def create_tcpip_message(socket_: socket.socket, id_: bytes, sequence_number: int, flags: list, data: str):
    sequence_number = sequence_number.to_bytes(2, "big")
    source_port     = (socket_.getsockname()[1]).to_bytes(2, "big")
    dst_port        = (socket_.getpeername()[1]).to_bytes(2, "big")

    source_address  = (socket_.getsockname()[0]).split('.')
    out = b''
    for bit in source_address:
        out += (int(bit).to_bytes(1, "big"))
    source_address = out

    dst_address = (socket_.getpeername()[0]).split('.')
    out = b''
    for bit in dst_address:
        out += (int(bit).to_bytes(1, "big"))
    dst_address = out

    flag = '000000000'
    for flag_ in flags:
        flag = add_bin(flag, flag_)
    # phase 1
    do_rsv_flags = int('1111' + '000' + flag, 2).to_bytes(2, "big")
    tcp_header = create_tcp_header(source_port, dst_port, sequence_number, do_rsv_flags, bytes(2))
    pseudo_header = create_pseudo_header(source_address, dst_address, len(tcp_header + data.encode()).to_bytes(2, "big"))
    data_offset = bin(int(len(tcp_header + data.encode()) / 4)).removeprefix('0b')
    # phase 2
    do_rsv_flags = int(data_offset + '000' + flag, 2).to_bytes(2, "big")
    tcp_checksum = binascii.crc_hqx((pseudo_header + tcp_header), 16).to_bytes(2, "big")
    # tcp_checksum = checksum(str(pseudo_header + tcp_header)).to_bytes(2, "big")
    ip_header = create_ip_header(bytes(2), id_, bytes(2), source_address, dst_address)
    total_length = len(ip_header + tcp_header).to_bytes(2, "big")
    ip_header = create_ip_header(total_length, id_, bytes(2), source_address, dst_address)
    # ip_checksum = checksum(str(ip_header)).to_bytes(2, "big")
    ip_checksum = binascii.crc_hqx(ip_header, 16).to_bytes(2, "big")
    # phase 3
    tcp_header = create_tcp_header(source_port, dst_port, sequence_number, do_rsv_flags, tcp_checksum)
    ip_header = create_ip_header(total_length, id_, ip_checksum, source_address, dst_address)

    tcp_ip_message = ip_header + tcp_header + data.encode()
    return tcp_ip_message


def create_pseudo_header(source_address: bytes, dst_address: bytes, tcp_len: bytes) -> bytes:
    """
    :param source_address:  4 bytes
    :param dst_address:     4 bytes
    :param tcp_len:         amount of bytes from source port to urgent pointer including data 2 bytes
    :return:
    """
    pseudo_header = b'\x00\x06'
    pseudo_header += source_address
    pseudo_header += dst_address
    pseudo_header += tcp_len
    return pseudo_header


def create_tcp_header(source_port: bytes, dst_port: bytes, sequence_number: bytes, do_rsv_flags: bytes, checksum_: bytes) -> bytes:
    """Data offset is number of bytes in tcp header divided by 4
    do_rsv_flags is 1 word combined of 4 bits for data off set + 3 bits of 0 and 9 bits of flag no"""
    tcp_header = source_port            # Port (2 bytes)
    tcp_header += dst_port              # Port (2 bytes)
    tcp_header += sequence_number       # Sequence Number - increased each message (4 bytes)
    tcp_header += b'\x00\x00\x00\x00'   # ACK Number (4 bytes)
    tcp_header += do_rsv_flags          # Data offset + rcv + flags (2 bytes)
    tcp_header += b'\xff\xff'           # Window size
    tcp_header += checksum_              # checksum (2 bytes)
    tcp_header += b'\x00\x00'           # urgent_pointer
    return tcp_header


def create_ip_header(total_length: bytes, id_: bytes, checksum_: bytes, source_address: bytes, dst_address: bytes) -> bytes:
    """
    :param total_length:    2 bytes tcp + ip
    :param id_:             2 bytes
    :param checksum_:       2 bytes
    :param source_address:  4 bytes
    :param dst_address:     4 bytes
    :return:
    """
    ip_header = b'\x45\x00'         # Version/IHL/Type of service
    ip_header += total_length       # Adding length (2 bytes)
    ip_header += id_                # ID (2 bytes)
    ip_header += b'\x00\x00'        # flags + fragment offset
    ip_header += b'\x40\x06'        # TTL + protocol    https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers
    ip_header += checksum_           # checksum (2 bytes)
    # ip_header += source_address     # IP (4 bytes)
    # ip_header += dst_address        # IP (4 bytes)
    print(total_length)
    print(id_)
    print(checksum_)
    return ip_header


def checksum(header: str) -> hex:
    """:param header is a string of bytes you want to count check sum_ from"""
    header = str(header).removeprefix("b'").removesuffix("'")
    header = header.split(r"\x")
    out = []
    for byte_ in header:
        match len(byte_):
            case 0:
                continue
            case 1:
                out.append((hex(ord(byte_))).removeprefix('0x'))
            case 2:
                out.append(byte_)
            case _:
                out.append(byte_[:2])
                for i in range(2, len(byte_)):
                    out.append((hex(ord(byte_[i]))).removeprefix('0x'))
    sum_ = 0x0000
    for i in range(int(len(out) / 2)):
        word = '0x' + out[i * 2] + out[i * 2 + 1]
        sum_ += literal_eval(word)
    while sum_ > literal_eval('0xffff'):
        sum_ = (sum_ - literal_eval('0x10000')) + + literal_eval('0x0001')
    checksum_ = literal_eval('0xffff') - sum_
    return checksum_


def calculate_checksum(header: bytes) -> int:
    """Calculate the checksum for the given header."""
    words = [int(header[i:i+2], 16) for i in range(0, len(header), 2)]

    # Sum all 16-bit words
    total = sum(words)

    # Add the carry if there is any
    while total > 0xFFFF:
        total = (total & 0xFFFF) + (total >> 16)

    # Calculate the one's complement
    checksum = 0xFFFF - total

    return checksum


# flags ip:
# 111 - Network Control
# 110 - Internetwork Control
# 101 - CRITIC / ECP
# 100 - Flash Override
# 011 - Flash
# 010 - Immediate
# 001 - Priority
# 000 - Routine

