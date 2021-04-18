# RoboCoRS Unified Codebase

Unified codebase for the senior project course, EEE 493/4: Industrial Design Project, at Bilkent University.

## Requirements

The `OpenCV` library is a requirement of the project. On ARM based systems, compilation from the [source](https://github.com/opencv/opencv) is required. Hence, this dependency is not included in the `setup.py` for the sake of generality. For Windows and UNIX-based operating systems, it can be simply installed with extra modules as follows.

`pip install opencv-contrib-python`

In addition, [Redis](https://redis.io/) must be installed for the system, in order to handle inter-process communication.