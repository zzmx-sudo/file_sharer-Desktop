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