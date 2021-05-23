from pathlib import Path
from setuptools import setup, find_packages


def read(relative: str) -> str:
    base: Path = Path(__file__).parent
    return base.joinpath(relative).read_text()


setup(
    name='lidar',
    version='0.2',
    author='Atahan Yorgancı',
    author_email='atahanyorganci@hotmail.com',
    packages=find_packages(where='lidar'),
    install_requires=["redis", "pyserial",
                      "rplidar", "click", "numpy"],
)
