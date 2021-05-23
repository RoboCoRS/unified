import click
import redis


@click.command()
@click.option('-s', '--scenario', default=None, type=int)
def main(scenario):
    client = redis.Redis()
    if scenario is None:
        client.delete('scenario')
    else:
        client.set('scenario', scenario)


if __name__ == "__main__":
    main()
