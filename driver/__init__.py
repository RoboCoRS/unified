from serial import Serial, STOPBITS_ONE
from dataclasses import dataclass
from enum import Enum
from time import sleep


RF = 10
RR = 15
LF = 20
LR = 25
STOP = 0
SPEED = 160
SPEED_TURN = 80


@dataclass
class DriveCommand:
    direction: int
    speed: int

    def __iter__(self):
        return iter([self.direction, self.speed])


class Driver:
    def __init__(self, port, *, baudrate=115200, bytesize=8, timeout=2, stopbits=STOPBITS_ONE):
        self.serial = Serial(port=port, baudrate=baudrate,
                             bytesize=bytesize, timeout=timeout, stopbits=stopbits)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop()
        self.serial.close()

    def turn_left(self):
        cmd = DriveCommand(LF, SPEED_TURN)
        print(cmd)
        self.serial.write(bytearray(cmd))
        sleep(0.1)
        cmd = DriveCommand(RF, SPEED)
        print(cmd)
        self.serial.write(bytearray(cmd))
        sleep(0.1)

    def turn_right(self):
        cmd = DriveCommand(LF, SPEED)
        print(cmd)
        self.serial.write(bytearray(cmd))
        sleep(0.1)
        cmd = DriveCommand(RF, SPEED_TURN)
        print(cmd)
        self.serial.write(bytearray(cmd))
        sleep(0.1)

    def drive_forward(self):
        cmd = DriveCommand(LF, SPEED)
        print(cmd)
        self.serial.write(bytearray(cmd))
        sleep(0.1)
        cmd = DriveCommand(RF, SPEED)
        print(cmd)
        self.serial.write(bytearray(cmd))
        sleep(0.1)

    def drive_backwards(self):
        cmd = DriveCommand(LR, SPEED)
        print(cmd)
        self.serial.write(bytearray(cmd))
        sleep(0.1)
        cmd = DriveCommand(RR, SPEED)
        print(cmd)
        self.serial.write(bytearray(cmd))
        sleep(0.1)

    def stop(self):
        cmd = DriveCommand(LF, STOP)
        print(cmd)
        self.serial.write(bytearray(cmd))
        sleep(0.1)
        cmd = DriveCommand(RF, STOP)
        print(cmd)
        self.serial.write(bytearray(cmd))
        sleep(0.1)
