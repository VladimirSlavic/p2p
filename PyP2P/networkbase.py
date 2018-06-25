from socket import *
from ssl import socket_error

class NetworkBase:

    CLIENT_PORT = 50007
    BOOTSTRAP_ADDRESS = '192.168.43.130'
    MESSAGE_TYPE = 'msg_type'
    BOOTSTRAP_RESPONSE = 'getaddr_response'
    IP_ADDRESSES = 'ip_addrs'
