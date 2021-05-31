from time import sleep, time
import os
from rplidar import RPLidar, RPLidarException
import click
import redis
from typing import Dict, Tuple, List
from serial.tools import list_ports
import numpy as np
from lidar.filter import Filter, FilterState, FilterDispatcher


class LidarRangeType(click.ParamType):
    name = 'LidarRange'

    def convert(self, value, param, ctx):
        try:
            name, range_str = tuple(value.split(':'))
            start, stop = tuple(range_str.split('-'))
            start = int(start) % 360
            stop = int(stop) % 360
        except TypeError:
            self.fail(
                "expected string for int() conversion, got "
                f"{value!r} of type {type(value).__name__}",
                param,
                ctx,
            )
        except ValueError:
            self.fail(
                f'LidarRange should be formatted in "NAME:START-STOP"', param, ctx)
        return name, start, stop


def get_device_com(comports, vid_pid_tuple: List[Tuple[int, int]]):
    device_com = [com.device for com in comports
                  if (com.vid, com.pid) in vid_pid_tuple]
    return device_com[0] if len(device_com) else None


DEBUG = False
LIDAR_VID_PID = [(4292, 60000)]
comports = list(list_ports.comports())
lidar_dev_com = get_device_com(comports, LIDAR_VID_PID)
client = redis.Redis()


@click.group()
def cli():
    pass


def time_it(func):
    if not DEBUG:
        return func

    size = os.get_terminal_size()
    col_count = size.columns

    def timed(*args, **kwargs):
        start = time() * 1e9
        result = func(*args, **kwargs)
        delta = time() * 1e9 - start
        out = f'{func.__name__} took {delta:0.2f} ns to execute'
        print(out.ljust(col_count), end='\r')
        return result
    return timed


@time_it
def process_data(dispatcher, distance, angle):
    state, dist, angle, name = dispatcher.dispatch(distance, angle)
    if state == FilterState.VALID:
        client.set(f'{name}:dist', float(dist))
        client.set(f'{name}:angle', float(angle))
    elif state == FilterState.INVALID:
        client.delete(f'{name}:dist', f'{name}:angle')


@cli.command()
@click.option('--port', type=str, default=lidar_dev_com)
def stop(port):
    lidar = RPLidar(port)
    lidar.start_motor()
    sleep(0.01)
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()


@cli.command()
@click.argument('lidar_ranges', type=LidarRangeType(), nargs=-1)
@click.option('--port', type=str, default=lidar_dev_com)
def detect(lidar_ranges, port):
    lidar = RPLidar(port)
    lidar.start_motor()
    sleep(1)
    COUNT_LIMIT = 10

    dispatcher = FilterDispatcher(lidar_ranges, COUNT_LIMIT)
    try:
        for _, _, angle, distance in lidar.iter_measures(scan_type='normal',
                                                         max_buf_meas=4500):
            process_data(dispatcher, distance, angle)
    except RPLidarException as e:
        print(e)
    finally:
        lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()


@cli.command()
@click.argument('name')
def display(name):
    try:
        while True:
            dist = client.get(f'{name}:dist')
            angle = client.get(f'{name}:angle')
            if dist and angle:
                formatted = f'Distance({name}, distance={float(dist):0.2f}mm, angle={float(angle):0.2f}deg)     '
            else:
                formatted = f'Distance({name}, INVALID_DISTANCE)'
            print(formatted.ljust(40, ' '), end='\r')
            sleep(0.01)
    except KeyboardInterrupt:
        pass


cli()
