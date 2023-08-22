import uuid
import time


def generate_uuid() -> str:

    return str(uuid.uuid1())

def generate_timestamp() -> int:

    return int(time.time() * 1000)

result = generate_timestamp()
print(result)