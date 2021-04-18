from time import sleep
from rplidar import RPLidar, RPLidarException
import click
import redis
from typing import Dict, Tuple
from serial.tools import list_ports
import numpy as np


def get_device_com(comports, vid_pid_tuple: Tuple[int, int]):
    device_com = [com.device for com in comports
                  if (com.vid, com.pid) == vid_pid_tuple]
    return device_com[0] if len(device_com) else None


LIDAR_VID_PID = (4292, 60000)
comports = list(list_ports.comports())
lidar_dev_com = get_device_com(comports, LIDAR_VID_PID)
client = redis.Redis()


def in_angle(start, stop, angle) -> bool:
    if start < stop:
        return start < angle and angle < stop
    else:
        return start < angle or angle < stop


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

    try:
        measurements = np.zeros(COUNT_LIMIT, dtype=np.float32)
        measurement_count = 0
        close_count = 0
        for _, _, angle, distance in lidar.iter_measurments():
            if in_angle(start, stop, angle):
                if distance:
                    measurements[measurement_count] = distance
                    measurement_count += 1
                    if measurement_count >= COUNT_LIMIT:
                        min_dist = np.min(measurements)
                        measurement_count = close_count = 0
                        client.set('min', float(min_dist))
                        if verbose:
                            print(f'Min Dist: {min_dist:0.2f} mm   ', end='\r')
                else:
                    close_count += 1
                    if close_count == COUNT_LIMIT:
                        measurement_count = close_count = 0
                        client.delete('min')
                        if verbose:
                            print('Min Dist: Too close!   ', end='\r')
    except RPLidarException as e:
        print(e)
    finally:
        lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()


main()
