from subprocess import Popen, run, DEVNULL
from time import sleep
from pathlib import Path
from typing import List
import os
import psutil
import redis
import platform

k_DEBUG = True

if platform.system() == 'Windows':
    py_cmd = 'python'
else:
    py_cmd = 'python3'


def ignite_redis() -> psutil.Process:
    proc = Popen(['redis-server'],
                 stdout=DEVNULL,
                 stderr=DEVNULL)
    p = psutil.Process(proc.pid)
    return p


def ignite_helpers(helper_progs: List[List[str]]) -> List[psutil.Process]:
    procs = [Popen(prog) for prog in helper_progs]
    ps = [psutil.Process(proc.pid) for proc in procs]
    return ps


def ignite_controller(scenario_number: int,
                      controller_progs: List[Path]) -> psutil.Process:
    global py_cmd
    scenario_number = max(1, min(scenario_number, len(controller_progs)))
    prog = controller_progs[scenario_number - 1]
    proc = Popen([py_cmd, f'{prog}',
                  f'-s {scenario_number}'])
    p = psutil.Process(proc.pid)
    return p


def main(client: redis.Redis,
         controller_progs: List[Path],
         helper_progs: List[Path],
         debug):
    redis_p = ignite_redis()
    helper_ps = ignite_helpers(helper_progs)
    control_p = None
    old_scenario = None
    if debug:
        all_ps = []
        for p in helper_ps:
            all_ps.append(p)

    try:
        while True:
            new_scenario = client.get('scenario')
            new_scenario = None if new_scenario is None else int(new_scenario)

            if new_scenario is None:
                if control_p and control_p.is_running():
                    control_p.terminate()
                    sleep(0.01)
                    control_p = None

            elif new_scenario != old_scenario:
                if control_p and control_p.is_running():
                    control_p.terminate()
                    sleep(0.01)
                control_p = ignite_controller(new_scenario, controller_progs)
                if debug:
                    all_ps.append(control_p)

            old_scenario = new_scenario
            print(f'Scenario {old_scenario}:                ', end='\r')
            sleep(0.01)

    except:
        pass
    finally:
        for p in helper_ps:
            if p and p.is_running():
                p.terminate()
        if control_p and control_p.is_running():
            control_p.terminate()
        if redis_p and redis_p.is_running():
            run(['redis-cli', 'shutdown'],
                stdout=DEVNULL,
                stderr=DEVNULL)
            if redis_p and redis_p.is_running():
                redis_p.terminate()
        run([py_cmd, '-m', 'lidar', 'stop'])
        sleep(0.01)

        if debug:
            for ps in all_ps:
                print(ps)


if __name__ == '__main__':
    client = redis.Redis()

    cwd = Path.cwd()
    detector_prog = [py_cmd, '-m', 'detector', '0', '-s', '-q']
    lidar_prog = [py_cmd, '-m', 'lidar', 'detect',
                  'f:340-20',
                  'fl:320-340',
                  'fr:20-40',
                  'l:260-280',
                  'r:80-100']
    serial_prog = [py_cmd, os.path.join('scripts', 'serial_esp.py'),
                   'f:Front',
                   'fl:FrontLeft',
                   'fr:FrontRight',
                   'l:Left',
                   'r:Right']
    helper_programs = [detector_prog, lidar_prog, serial_prog]

    scenario1_path = Path.joinpath(cwd, '..', 'motorpwm', 'follower.py')
    scenario2_path = Path.joinpath(cwd, '..', 'motorpwm', 'keyboard_drive.py')
    scenario3_path = Path.joinpath(cwd, '..', 'motorpwm', 'controller.py')
    scenario4_path = Path.joinpath(cwd, '..', 'motorpwm', 'controller.py')
    scenario5_path = Path.joinpath(cwd, '..', 'motorpwm', 'hostile.py')

    controller_programs = [scenario1_path, scenario2_path,
                           scenario3_path, scenario4_path,
                           scenario5_path]

    main(client, controller_programs, helper_programs, k_DEBUG)
