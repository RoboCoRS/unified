# ESP32 - Video Streaming and Dashboard Module


ESP32 from Espressif is a feature-rich MCU with integrated Wi-Fi, in our project ESP32 is used to stream video feed, and LiDAR data from main microcontrollers. ESP32 microcontroller in our project serves a single base HTML file which continuously fetches data and updates the UI. The microcontroller receives data from its serial port at 256000 baud.

## Getting Started

### Mock Server

Base HTML served by the microcontroller is developed in a mock Flask server. To run Flask server install dependencies from `Pipenv` file located in the root of the project by running `pipenv install`, and run following commands.

- For bash
```shell
$ export FLASK_APP="server"
$ export FLASK_ENV="development"
$ flask run
```

- For Powershell
```powershell
$env:FLASK_APP="server"
$env:FLASK_ENV="development"
flask run
```

Base HTML file can be exported using `dump` command by giving it a name.
```shell
$ flask dump "Rasputin"
```

### MCU

ESP32 source files are organized under a PlatformIO project.
