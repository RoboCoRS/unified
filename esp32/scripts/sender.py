from serial import Serial
import base64
import time
from sys import argv


def main():
    if len(argv) != 3:
        print('Usage: PORT IMAGE_PATH')
        return

    with open(argv[2], "rb") as image:
        content = image.read()

    with Serial(argv[1], baudrate=350000) as serial:
        while True:
            to_write = base64.b64encode(content)
            print(to_write)
            serial.write(to_write)
            serial.write('*'.encode('ascii'))
            time.sleep(1)


if __name__ == '__main__':
    main()
