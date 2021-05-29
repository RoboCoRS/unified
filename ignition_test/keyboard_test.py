from re import S
import keyboard
import redis
from time import sleep

client = redis.Redis()


def inc(scenario):
    global client
    if scenario is not None:
        client.set('scenario', min(scenario + 1, 5))


def dec(scenario):
    global client
    if scenario is not None:
        client.set('scenario', max(1, scenario - 1))


def drive(char: str):
    global client
    scenario = client.get('scenario')
    scenario = None if scenario is None else int(scenario)
    if char == 'd':
        inc(scenario)
    elif char == 'a':
        dec(scenario)
    sleep(0.01)


def keyboard_control():
    try:
        keyboard.wait()
    except:
        drive('q')


if __name__ == "__main__":
    keyboard.add_hotkey('a', drive, args=('a'))
    keyboard.add_hotkey('d', drive, args=('d'))
    keyboard.add_hotkey('q', drive, args=('q'))
    keyboard_control()
