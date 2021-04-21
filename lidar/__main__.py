from time import sleep
from rplidar import RPLidar, RPLidarException
import click
import redis
from typing import Dict, Tuple
from serial.tools import list_ports
import numpy as np
from lidar.filter import Filter, FilterState


def get_device_com(comports, vid_pid_tuple: Tuple[int, int]):
    device_com = [com.device for com in comports
                  if (com.vid, com.pid) == vid_pid_tuple]
    return device_com[0] if len(device_com) else None


def in_angle(start, stop, angle) -> bool:
    if start < stop:
        return start < angle and angle < stop
    else:
        return start < angle or angle < stop


def print_min(dist: float, angle: float):
    d = f'{dist:0.2f} mm'.rjust(11)
    a = f'{angle:0.2f} deg'.rjust(10)
    print(f'Min Dist: {d} {a}', end='\r')


LIDAR_VID_PID = (4292, 60000)
comports = list(list_ports.comports())
lidar_dev_com = get_device_com(comports, LIDAR_VID_PID)
client = redis.Redis()


@click.command()
@click.argument('start', type=click.INT)
@click.argument('stop', type=click.INT)
@click.option('--port', type=str, default=lidar_dev_com)
@click.option('-v', '--verbose', is_flag=True)
def main(start, stop, port, verbose):
    lidar = RPLidar(port)
    lidar.start_motor()
    sleep(1)
    start = start % 360
    stop = stop % 360
    COUNT_LIMIT = 10

    myfilter = Filter(COUNT_LIMIT)
    try:
        for _, _, angle, distance in lidar.iter_measurments():
            if in_angle(start, stop, angle):
                state, dist, angle = myfilter.enqueue(distance, angle)
                if state == FilterState.VALID:
                    client.set('min', float(dist))
                    if verbose:
                        print_min(dist, angle)
                elif state == FilterState.INVALID:
                    client.delete('min')
                    if verbose:
                        print('Min Dist: Invalid distance!           ', end='\r')
    except RPLidarException as e:
        print(e)
    finally:
        lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()


main()
