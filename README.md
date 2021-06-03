# RoboCoRS Unified Codebase

Unified codebase for the senior project course, EEE 493/4: Industrial Design Project, at Bilkent University.

## Table of Contents

  - [Acknowledgement](#acknowledgement)
  - [Aim](#aim)
  - [Project Structure](#project-structure)
  - [Software Requirements for Main Microcontroller](#software-requirements-for-main-microcontroller)
    - [x86](#x86)
    - [ARM](#arm)
  - [Software Requirements for Peripheral Devices](#software-requirements-for-peripheral-devices)
  - [Hardware Requirements](#hardware-requirements)
  - [Usage of Modules](#usage-of-modules)
    - [detector](#detector)
    - [lidar](#lidar)
  - [Simple Usage](#simple-usage)

## Acknowledgement

- This project was realized in cooperation with ROKETSAN.
- 
  :uk: This project was supported by TUBITAK under the 2209-B program.<br>
  :tr: Bu çalışma 2209-B programı kapsamında TÜBİTAK tarafından desteklenmiştir.

## Aim
In this project autonomous mobile robots with heterogeneous hardware configurations are developed for collective task execution without communication between the robots, or global mapping systems. Collective tasks such as converging on a predefined target will be executed with three robots with different hardware configurations. Without communication (i.e. RF, LoRa) between robots, and global localization systems (i.e. GPS), robots make use of both visual data from cameras, and distance data from LiDAR to local mapping of their environment. Visual, and distance data is used to further augmented with object identification, and localization so that robots can identify obstacles, peer robots, and objectives in the environment. Local mapping of the environment is then used by a custom obstacle avoidance algorithm to perform collective task execution. The robots' collective ability to execute common objectives will be evaluated using five different scenarios. These scenarios are 

1. Target Identification and Transition with One Robot 
2. Pioneer Robot Following, 
3. Target Identification and Locating with Three Robots, 
4. Target Identification and Transition with Three Robots While Avoiding Obstacles 
5. Hostile Target Detection and Avoiding. 
   
These scenarios test robots’ ability to identify a predefined target, and converge on the said target using  local mapping of the environment. More challenging problems such as path finding in an environment with obstacles, are solved using custom grid-based obstacle avoidance algorithm. Developed systems such as object identification, and path finding are required  to run in parallel.  For process orchestration, and lightweight message passing Redis will be used, for low memory footprint, and low communication overhead. More detailed information like equipment list, searching algorithms, target and peer detection preferences, etc. provided in [docs/report.pdf](./docs/report.pdf)  

## Project Structure

The project consists of pre-defined five scenarios. The actions that we take in the light of same information varies between these scenarios, but we need to obtain camera and LiDAR feed and stream them for each scenario. In this context, we are running `detector` and `lidar` modules along with the [ESP32 serial communication script](./scripts/serial_esp.py) in the background. These modules are continuously fulfilling their tasks and writing necessary information to the running `redis-server` on the device. Then, the running motor controller script, for the selected scenario, takes action according to the information on the `redis-server`.

## Software Requirements for Main Microcontroller

A lightweight database system [Redis](https://redis.io/) must be installed, in order to handle inter-process communication. The `OpenCV` library is a requirement of the project. On ARM based systems, compilation from the [source](https://github.com/opencv/opencv) is required. Hence, this dependency is not included in the `Pipfile` or `requirements.txt` for the sake of generality. Therefore, we recommend the following steps for `x86` and `ARM` architectures respectively for installing necessary requirements.

### x86

1. Install [Redis](https://redis.io/) for your system.
2. Obtain appropriate version of `Python`.
3. We recommend using a virtual environment with the help of `pipenv`. Install `pipenv` using 
   
   ```shell
   $ pip install --user pipenv
   ```

4. Clone this project and `cd` into it.
5. Create a virtual environment with the command 
   
   ```shell
   $ pipenv shell
   ```
    
6. Install necessary packages with the command
   
   ```shell
   $ pipenv install
   ```
    
7. Install `OpenCV` additionally with the command
   
   ```shell
   $ pipenv install opencv-contrib-python
   ```

### ARM

1. Download and build `OpenCV` from the [source](https://github.com/opencv/opencv) with the extra modules.
2. Install [Redis](https://redis.io/) for your system.
3. Obtain appropriate version of `Python`.
4. Clone this project and `cd` into it.   
5. Install necessary packages with the command
   
   ```shell
   $ pip install -r requirements.txt
   ```

## Software Requirements for Peripheral Devices

The main controller of the system communicates with several devices to accomplish the necessary tasks. Two of these devices, `Arduino Nano` and `ESP32` must be individually programmed so that they can perform their tasks. For this project, we utilized PlatformIO to program these devices but any alternative is plausible. Program `Arduino Nano` with [motor_controller/serial_pwm_driver.ino](./motor_controller/serial_pwm_driver.ino) and `ESP32` with [esp32/src/main.cpp](./esp32/src/main.cpp). Detailed information for `ESP32` is present in its own [README](./esp32/README.md).

## Hardware Requirements

For the entirety of the program a camera must be connected to the main controller for detection and tracking of both the target and the peers. `RPLIDAR` must be connected to the main controller with a data cable and must be powered appropriately for obstacle avoidance. An `Arduino Nano` must be connected to the main controller for the serial communication of motor controlling. DC motors must be connected to the `Arduino Nano` for logic operations and they must be connected to an appropriate power source. Finally, the main controller must be connected to the `ESP32` for live camera and LiDAR feed and for switching between multiple scenarios. 

- Note that the provided code recognizes these devices by identifying them from their `(VID, PID)` pairs. For this project the utilized components have unique pairs, so it did not create a problem. For some `Arduino` clones these pairs can have the same values with `ESP32`, which can cause problems with device identification.

## Usage of Modules

In order to use the modules, the `redis-server` must be running in the background. If [Redis](https://redis.io/) is successfully installed on your system, running the following command in your terminal starts the on device server.

```shell
$ redis-server
``` 

There are two main modules in the project that can be run `detector` and `lidar`. These modules can be run separately, although the `redis-server` must be running in the background. The specifications of these modules are described below.

### detector

The detector module takes the device number as an argument. If there are multiple cameras are present in the system you can extend the program by running the detector module several times with different device IDs. The first and default device ID is `0`. The `frame-size` optional argument takes a dimensions separated by an `x` in the form of `WIDTHxHEIGHT`, e.g., `640x480`, which adjusts the proportions of the camera feed. It uses cameras default dimensions if nothing is passed for this option. The `serial` option enables the `detector` module to write the current frame to `redis-server`, so that the [ESP32 serial communication script](./scripts/serial_esp.py) can forward it to `ESP32`. Then we have the `display` and `quiet` options. By default the module displays the center point of the target and the current FPS value in the terminal, since during the scenarios there is no need to waste resources to display the camera feed on device, where we should only interact with the robots from the `ESP32`. For debug purposes the module provides `display` option to display real-time camera feed on device. Finally the `quite` option eliminates the default output provided in the terminal. 

```
Usage: python -m detector [OPTIONS] DEVICE

Options:
  --frame-size TEXT
  -d, --display
  -s, --serial
  -q, --quiet
  --help             Show this message and exit.
```

### lidar

`NAME:START-STOP`

```
Usage: python -m lidar [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  detect
  display
  stop
```

```
Usage: python -m lidar detect [OPTIONS] [LIDAR_RANGES]...

Options:
  --port TEXT
  --help       Show this message and exit.
```

```
Usage: python -m lidar display [OPTIONS] NAME

Options:
  --help  Show this message and exit.
```

## Simple Usage

We provided a script, `ignition.py`, to initiate every helper program, then the user can set the desired scenario with the [scenario changer script](./scripts/scenario_changer.py) if device access present, or from the client service that can be accessed by connecting to the host on `ESP32`. The `ignition.py` starts the `detector` and `lidar` modules as separate processes along with the [ESP32 serial communication script](./scripts/serial_esp.py) in the background. If a scenario selection is detected, `ignition.py` kills the on-going scenario script's process, if there is an on-going scenario, and creates a new process with the selected scenario's script. When all the requirements are satisfied, and all the hardware connections are correct, the user can simply start the whole project with the following command.
```
python ignition.py
```
This script starts the program with the default values of the modules and starts streaming on the `ESP32`.