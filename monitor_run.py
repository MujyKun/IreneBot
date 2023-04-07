"""
monitor_run.py

Monitor the bots memory usage and restart if the bot uses more than the max memory usage.
This is helpful to make sure the OS doesn't kill the bots process

In addition, this is helpful against memory leaks within the process itself.
Since the bots entire architecture has been changed in a short amount of time,
there is plenty of room for mistakes made in code.

Only use this run file if the bot has been using an excess amount of memory after a while
and a cache reset wouldn't help with that.
"""

import shutil
import psutil
import subprocess
import time

MAX_MEMORY_USAGE = 4096 * 1024 * 1024  # 4,096 MB


def monitor_process():
    # Get path to poetry executable
    poetry_path = shutil.which('poetry')
    if not poetry_path:
        raise RuntimeError('Poetry executable not found')

    while True:
        process = subprocess.Popen([poetry_path, 'run', 'python', 'main.py'])
        while True:
            if psutil.pid_exists(process.pid):
                mem_info = psutil.Process(process.pid).memory_info()
                print(f"Current Process Memory Usage: {mem_info.rss / (1024 ** 2)} (MBs)")
                if mem_info.rss > MAX_MEMORY_USAGE:
                    process.kill()
                    break
                time.sleep(60)
            else:
                break


if __name__ == '__main__':
    monitor_process()
