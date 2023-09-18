import time
import socket
import random

import uuid

def generate_uuid() -> str:

    return str(uuid.uuid1()).replace("-", "")

def generate_timestamp() -> int:

    return int(time.time() * 1000)

def get_local_ip() -> str:

    return socket.gethostbyname(socket.gethostname())

def generate_ftp_passwd() -> str:

    base_str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

    return "".join(random.sample(base_str, 5))

def exists_port(port: int) -> bool:

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)
        sock.connect((get_local_ip(), port))
        sock.close()
        return True
    except:
        return False

def generate_http_port(start_port: int) -> int:
    if start_port <= 1024:
        start_port = 8080

    if exists_port(start_port):
        start_port += 1
        return generate_http_port(start_port)
    else:
        return start_port