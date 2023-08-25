import time
import socket

import uuid

def generate_uuid() -> str:

    return str(uuid.uuid1()).replace("-", "")

def generate_timestamp() -> int:

    return int(time.time() * 1000)

def get_local_ip() -> str:

    return socket.gethostbyname(socket.gethostname())

result = get_local_ip()
print(result, type(result))