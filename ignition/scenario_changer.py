import click
import redis


@click.command()
@click.option('-s', '--scenario', default=1)
def main(scenario):
    client = redis.Redis()
    client.set('scenario', scenario)


if __name__ == "__main__":
    main()
