import sys
from time import sleep
import click


@click.command()
@click.option('-s', '--scenario', default=1)
def main(scenario):
    try:
        i = 0
        while True:
            print(f'Scenario {scenario}: {i}           ', end='\r')
            i += 1
            sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
