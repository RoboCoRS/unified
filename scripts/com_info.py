from serial.tools import list_ports
from pathlib import Path
import json
import os
import click


class USBdevice:

    def __init__(self, port_info):
        self.device = port_info.device
        self.name = port_info.name
        self.description = port_info.description
        self.hwid = port_info.hwid
        self.vid = port_info.vid
        self.pid = port_info.pid
        self.serial_number = port_info.serial_number
        self.location = port_info.location
        self.manufacturer = port_info.manufacturer
        self.product = port_info.product
        self.interface = port_info.interface

    def __repr__(self) -> str:
        return f'device\t\t: {self.device}\n' \
            f'name\t\t: {self.name}\n' \
            f'description\t: {self.description}\n' \
            f'hwid\t\t: {self.hwid}\n' \
            f'vid\t\t: {self.vid}, x"{self.vid:X}"\n' \
            f'pid\t\t: {self.pid}, x"{self.pid:X}"\n' \
            f'serial_number\t: {self.serial_number}\n' \
            f'location\t: {self.location}\n' \
            f'manufacturer\t: {self.manufacturer}\n' \
            f'product\t\t: {self.product}\n' \
            f'interface\t: {self.interface}\n' \


    def get_json(self):
        return json.dumps(self.__dict__, indent=4)


def write_comports_json(file_path: Path,
                        json_str: str, count: int):
    with open(file_path, 'w') as file:
        if count == 1:
            file.write(json_str)
        else:
            file.write('[\n' + json_str + '\n]')
        file.truncate()


@click.command()
@click.option('-o', '--output-json', default='devices.json',
              type=Path,
              help='Output json file for COM Port Info.')
@click.option('-v', '--verbose', count=True)
def main(output_json, verbose):
    root = os.path.dirname(__file__)
    comports = list(list_ports.comports())
    comport_count = len(comports)

    if 0 < comport_count:
        comps_json_str = []
        for c in comports:
            usb_dev = USBdevice(c)
            if 2 <= verbose:
                print(usb_dev, end='\n\n')
            json_str = usb_dev.get_json()
            comps_json_str.append(json_str)

        json_file_path = Path(os.path.join(root, output_json))
        write_comports_json(json_file_path,
                            ',\n'.join(comps_json_str),
                            comport_count)
        if verbose:
            print(f'[INFO]: Device info added to {json_file_path}')
    else:
        print('[WARN]: No suitable COM Port can be found.')


if __name__ == "__main__":
    main()
