from pathlib import Path
from typing import Dict, Tuple
from serial.tools import list_ports
from pathlib import Path
import click
import json
import os


def get_device_com(comports, vid_pid_tuple: Tuple[int, int]):
    device_com = [com.device for com in comports
                  if (com.vid, com.pid) == vid_pid_tuple]
    return device_com[0] if len(device_com) else None


def write_device_com_json(file_path: Path,
                          device_coms: Dict[str, str]):
    with open(file_path, 'w') as file:
        json.dump(device_coms, file, indent=4)


@click.command()
@click.option('-o', '--output-json',
              default=Path(os.path.dirname(__file__),
                           'serial_com_info.json'),
              type=Path,
              help='Output json file for COM Port Info.')
@click.option('-v', '--verbose', count=True)
def main(output_json, verbose):
    VID_PID = {
        'ardun': (1027, 24577),
        'lidar': (4292, 60000),
        'esp32': (6790, 29987),
    }
    comports = list(list_ports.comports())
    device_coms = {k: get_device_com(comports, v)
                   for k, v in VID_PID.items()}
    if verbose:
        for dev, port in device_coms.items():
            print(f'{dev.upper()} at COM Port: {port}')
    write_device_com_json(output_json, device_coms)


if __name__ == "__main__":
    main()
