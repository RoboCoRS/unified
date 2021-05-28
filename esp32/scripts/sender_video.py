from serial import Serial
import base64
import time
import cv2
from sys import argv


def main():
    if len(argv) != 2:
        print('Usage: PORT')
        return

    cap = cv2.VideoCapture(0)

    with Serial("COM6", baudrate=700000) as serial:
        while True:
            _, frame = cap.read()
            frame = cv2.resize(frame, (120, 80))
            content = cv2.imencode('.jpg', frame)[1]
            to_write = base64.b64encode(content)
            print(to_write)
            serial.write(to_write)
            serial.write('*'.encode('ascii'))


if __name__ == '__main__':
    main()
