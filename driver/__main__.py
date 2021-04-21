import click
from driver import Driver
from time import sleep


@click.group()
def cli():
    pass


@cli.command()
@click.argument('port', type=str)
def keyboard(port):
    with Driver(port) as driver:
        print('Turning left')
        driver.turn_left()
        sleep(5)
        print('Turning right')
        driver.turn_right()
        sleep(5)
        print('Driving forward')
        driver.drive_forward()
        sleep(5)
        print('Driving backwards')
        driver.drive_backwards()
        sleep(5)


cli()
