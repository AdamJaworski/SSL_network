import socket


def get_protocol(server: tuple) -> socket.AddressFamily:
    try:
        host_info = socket.getaddrinfo(server[0], server[1])
    except socket.error as error:
        print(f"[Warning] Couldn't gather host info! {error}")
        return socket.AddressFamily.AF_UNSPEC
    host_info = host_info[0]
    print(f'[Info] Successfully recognized host protocol {host_info[4]}')
    return host_info[0]



# hello = bytearray([3, 3])               # Version: TLS 1.2
#
# hello += bytearray([0]*32)              # Random
#
# hello += bytearray([
#     0,                                  # Session ID Length
#
#     0, 6,                               # Cipher Suites Length
#     0xc0, 0x2f,                         # TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
#     0, 0x2f,                            # TLS_RSA_WITH_AES_128_CBC_SHA
#     0, 0x39,                            # TLS_DHE_RSA_WITH_AES_256_CBC_SHA
#
#     1,                                  # Compression Methods Length: 1
#     0,                                  # Compression Method: null
#
#     0, 0                                # Extensions Length
# ])
#
# msg = bytearray([1])                    # Handshake Type: Client Hello
# msg += bytearray([0, 0, len(hello)]) + hello
#
# record = bytearray([
#     0x16,                               # Content Type: Handshake
#     3, 3                                # Version TLS 1.2
# ])
# record += bytearray([0, len(msg)]) + msg\

