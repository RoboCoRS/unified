from subprocess import Popen, DEVNULL
from time import sleep
from pathlib import Path
from typing import List
import psutil
import redis

k_DEBUG = True


def ignite_redis() -> psutil.Process:
    proc = Popen(['redis-server'],
                 stdout=DEVNULL,
                 stderr=DEVNULL)
    p = psutil.Process(proc.pid)
    return p


def ignite_helpers(helper_progs: List[Path]) -> List[psutil.Process]:
    procs = [Popen(['/usr/bin/python3', f'{prog}'],
                   stdout=DEVNULL,
                   stderr=DEVNULL)
             for prog in helper_progs]
    ps = [psutil.Process(proc.pid) for proc in procs]
    return ps


def ignite_controller(scenario_number: int,
                      controller_progs: List[Path]) -> psutil.Process:
    scenario_number = max(1, min(scenario_number, len(controller_progs)))
    prog = controller_progs[scenario_number - 1]
    proc = Popen(['/usr/bin/python3', f'{prog}',
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
                    control_p.kill()
                    sleep(0.01)
                    control_p = None
                print(f'Scenario {None}:                ', end='\r')
            elif new_scenario != old_scenario:
                if control_p and control_p.is_running():
                    control_p.terminate()
                    control_p.kill()
                    sleep(0.01)
                control_p = ignite_controller(new_scenario, controller_progs)
                if debug:
                    all_ps.append(control_p)

            old_scenario = new_scenario
            sleep(0.01)

    except KeyboardInterrupt:
        for p in helper_ps:
            if p and p.is_running():
                p.terminate()
                p.kill()
        if control_p and control_p.is_running():
            control_p.terminate()
            control_p.kill()
        if redis_p and redis_p.is_running():
            redis_p.terminate()
            redis_p.kill()
        sleep(0.01)

        if debug:
            for ps in all_ps:
                print(ps)


if __name__ == '__main__':
    client = redis.Redis()

    cwd = Path.cwd()
    detector_path = Path.joinpath(cwd, 'program1.py')
    lidar_path = Path.joinpath(cwd, 'program1.py')
    serial_path = Path.joinpath(cwd, 'program1.py')
    helper_programs = [detector_path, lidar_path, serial_path]

    scenario1_path = Path.joinpath(cwd, 'controller.py')
    scenario2_path = Path.joinpath(cwd, 'controller.py')
    scenario3_path = Path.joinpath(cwd, 'controller.py')
    scenario4_path = Path.joinpath(cwd, 'controller.py')
    scenario5_path = Path.joinpath(cwd, 'controller.py')

    controller_programs = [scenario1_path, scenario2_path,
                           scenario3_path, scenario4_path,
                           scenario5_path]

    main(client, controller_programs, helper_programs, k_DEBUG)
