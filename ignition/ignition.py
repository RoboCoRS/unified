from subprocess import Popen
from time import sleep
import psutil
from pathlib import Path
from typing import List, Tuple
import redis


def ignite_helpers(helper_progs: List[Path]) \
    -> Tuple[List[Popen],
             List[psutil.Process]]:
    procs = [Popen(['/usr/bin/python3', f'{prog}'])
             for prog in helper_progs]
    ps = [psutil.Process(proc.pid) for proc in procs]
    return procs, ps


def ignite_controller(scenario_number: int,
                      controller_progs: List[Path]) \
        -> Tuple[Popen, psutil.Process]:
    prog = controller_progs[scenario_number]
    proc = Popen(['/usr/bin/python3', f'{prog}',
                  f'-s {scenario_number}'])
    p = psutil.Process(proc.pid)
    return proc, p


def main(client: redis.Redis,
         controller_progs: List[Path],
         helper_progs: List[Path]):
    helper_procs, helper_ps = ignite_helpers(helper_progs)
    control_proc, control_p = None, None
    old_scenario = None

    try:
        while True:
            new_scenario = client.get('scenario')
            new_scenario = None if new_scenario is None else int(new_scenario)
            if new_scenario is None:
                if control_p and control_p.is_running():
                    control_p.terminate()
                    control_p.kill()
            elif new_scenario != old_scenario:
                if control_p and control_p.is_running():
                    control_p.terminate()
                    control_p.kill()
                control_proc, control_p = \
                    ignite_controller(new_scenario, controller_progs)

            old_scenario = new_scenario
            sleep(0.01)

    except KeyboardInterrupt:
        for p in helper_ps:
            if p.is_running():
                p.terminate()
                p.kill()
        if control_p.is_running():
            control_p.terminate()
            control_p.kill()

        print(helper_ps)
        print(control_p)


if __name__ == '__main__':
    client = redis.Redis()
    client.set('scenario', 1)

    cwd = Path.cwd()
    detector_path = Path.joinpath(cwd, 'program1.py')
    lidar_path = Path.joinpath(cwd, 'program1.py')
    serial_path = Path.joinpath(cwd, 'program1.py')

    scenario1_path = Path.joinpath(cwd, 'controller.py')
    scenario2_path = Path.joinpath(cwd, 'controller.py')
    scenario3_path = Path.joinpath(cwd, 'controller.py')
    scenario4_path = Path.joinpath(cwd, 'controller.py')
    scenario5_path = Path.joinpath(cwd, 'controller.py')

    helper_programs = [detector_path, lidar_path, serial_path]

    controller_programs = [scenario1_path, scenario2_path,
                           scenario3_path, scenario4_path,
                           scenario5_path]

    main(client, controller_programs, helper_programs)
