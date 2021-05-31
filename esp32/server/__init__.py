from flask import Flask, render_template, request, redirect
from typing import Optional, Tuple
from serial import Serial
import click
import os
import getpass
import socket
import base64
import cv2
import re
import random

app = Flask(__name__)
cap = cv2.VideoCapture(0)


def get_context(*, name=None, interval=None):
    SCENARIOS = [
        'Stop Execution',
        'Target Identification and Transition with One Robot',
        'Pioneer Robot Following',
        'Target Identification and Locating with Three Robots',
        'Target Identification and Transition with Three Robots While Avoiding Obstacles',
        'Hostile  Target  Detection  and  Avoiding',
    ]
    INTERVAL = 100 if interval is None else interval
    SCENARIOS = [{'name': scenario, 'index': i}
                 for i, scenario in enumerate(SCENARIOS)]
    NAME = name if name is not None else f'{getpass.getuser()}@{socket.gethostname()}'
    return {
        'scenarios': SCENARIOS,
        'interval': INTERVAL,
        'name': NAME
    }


def get_image(*, size: Optional[Tuple[int, int]] = None) -> str:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    if size is not None:
        frame = cv2.resize(frame, size)
    content = cv2.imencode('.jpg', frame)[1]
    return base64.b64encode(content)


def get_data():
    data = [('Front', 6000, 3),
            ('Front Left', 3900, 325),
            ('Front Right', 4000, 36),
            ('Left', 4200, 275),
            ('Right', 4100, 80)]
    out = []
    for name, dist, angle in data:
        out.append((name, dist + 20 * random.random(),
                   angle + 5 * random.random()))
    return out


if app.config['DEBUG']:
    CONTEXT = get_context(interval=100)
else:
    CONTEXT = get_context(interval=16, name='GroupB4')


@app.cli.command('dump', help='Dump HTML template as C++ header file to stdout')
@click.argument('name', type=str)
@click.option('--interval', type=int, default=None)
def dump(name, interval):
    context = get_context(name=name, interval=interval)
    content = render_template('index.jinja', **context)

    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'"', '\\"', content)
    content = content.strip()

    print('#pragma once')
    print()
    print('#include <Arduino.h>')
    print()
    print(f'const String DEVICE_NAME = "{name}";')
    print(f'const String BASE_HTML = "{content}";')


@app.cli.command('serial', help='Print default video capture to serial port')
@click.argument('port', type=str)
@click.argument('baudrate', type=int)
def dump(port, baudrate):
    try:
        with Serial(port, baudrate=baudrate) as serial:
            while True:
                image = get_image(size=(120, 80))
                serial.write(image)
                serial.write('*'.encode('ascii'))
    except KeyboardInterrupt:
        pass


@app.route('/')
def index():
    return render_template('index.jinja', **CONTEXT)


@app.route('/pic')
def pic():
    if app.config['DEBUG']:
        return get_image(size=(120, 80))
    else:
        return get_image()


@app.route('/scenario')
def scenario():
    if "index" not in request.args:
        return redirect('/')

    index = request.args["index"]
    app.logger.info(f'Selecting Scenario {index}')
    return redirect(f'/?index={index}')


@app.route('/lidar')
def lidar():
    data = get_data()
    return ';'.join(f'{name}-{dist:0.2f}-{angle:0.2f}' for name,  dist, angle in data)
