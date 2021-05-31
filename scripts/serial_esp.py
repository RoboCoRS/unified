from serial import Serial
import redis
from serial.tools import list_ports
from typing import Dict, Tuple, List
import click


class ESPRangeType(click.ParamType):
    name = 'LidarRange'

    def convert(self, value, param, ctx):
        try:
            name, disp_name = tuple(value.split(':'))
        except ValueError:
            self.fail(
                f'LidarRange should be formatted in "NAME:DISPLAY NAME"', param, ctx)
        return name, disp_name


ESP32_VID_PID = [(6790, 29987)]


def get_device_com(comports, vid_pid_tuple: List[Tuple[int, int]]):
    device_com = [com.device for com in comports
                  if (com.vid, com.pid) in vid_pid_tuple]
    return device_com[0] if len(device_com) else None


@click.command()
@click.argument('lidar_ranges', type=ESPRangeType(), nargs=-1)
def main(lidar_ranges):
    global ESP32_VID_PID
    client = redis.Redis()

    comports = list(list_ports.comports())
    esp32_dev_com = get_device_com(comports, ESP32_VID_PID)
    names = [name for name, _ in lidar_ranges]
    disp_names = [disp_name for _, disp_name in lidar_ranges]
    dists_str = [f'{name}:dist' for name in names]
    angles_str = [f'{name}:angle' for name in names]

    with Serial(esp32_dev_com, baudrate=256000) as serial:
        while True:
            serial_image = client.get('serial_image')
            if serial_image:
                dists = [0 if b is None else float(b)
                         for b in client.mget(dists_str)]
                angles = [0 if b is None else float(b)
                          for b in client.mget(angles_str)]

                s = [f'{name}-{dist:0.2f}-{angle:0.2f}'
                     for name, dist, angle in zip(disp_names, dists, angles)]
                lidar_info = ';'.join(s).encode('ascii')

                serial.write(serial_image)
                serial.write('*'.encode('ascii'))
                serial.write(lidar_info)
                serial.write('*'.encode('ascii'))

            if serial.in_waiting:
                num = int.from_bytes(serial.read(), 'big')
                if 0 < num < 6:
                    print(f'Switching to scenario {num}      ')
                    client.set('scenario', num)
                else:
                    print('Stopping ...    ')
                    client.delete('scenario')


if __name__ == "__main__":
    main()
