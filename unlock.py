#!/usr/bin/env python3
from datetime import datetime as Datetime
from datetime import time as Time
import os


SUDO_FILE_PATH = "/etc/sudoers.d/x"
SUDO_FILE_CONTENT = "x ALL=(ALL:ALL) NOPASSWD:ALL"
SAFE_TIME_START = Time(4, 0)
SAFE_TIME_END = Time(18, 0)


def unlock():
    with open(SUDO_FILE_PATH, "w") as sudoers:
        sudoers.write(SUDO_FILE_CONTENT)


def is_safe_time():
    return SAFE_TIME_START <= Datetime.now().time() <= SAFE_TIME_END


if is_safe_time():
    unlock()
    print("UNLOCKED")
else:
    print("FORBIDDEN")
