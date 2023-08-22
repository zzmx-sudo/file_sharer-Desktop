import uuid
import time


def generate_uuid():

    return uuid.uuid1()

def generate_timestamp():

    return int(time.time() * 1000)

result = generate_timestamp()
print(result)