#!/usr/bin/env python3.8
"""
Smartlock

Usage:
    smartlock [options]

Options:
    -c --config=FILE       Default: DEFAULT_CONFIG_PATH
    -t --time=TIME         Default: now
       --datetime=DATE     Default: now
    -l --log-level=LEVEL   Default: DEFAULT_LOG_LEVEL
    -s --dry-run
"""
from typing import *
from dataclasses import dataclass
from docopt import docopt
from enum import Enum, auto
from datetime import datetime as Datetime
from datetime import time as Time
from datetime import date as Date
import datetime
import enum
import logging
import os
import yaml
import subprocess
import re


DEFAULT_CONFIG_PATH = "/etc/smartlock.yaml"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = '%(asctime)-15s %(levelname)s: %(message)s'


@dataclass
class Config:
    safe_time: str
    danger_time: str
    critical_time: str

    env: Optional[Dict[str, str]] = None
    remove_admin_rights: str = ""
    restore_admin_rights: str = ""
    terminate: str = ""

    date_fmt: Optional[str] = None
    disable_periods: Optional[List[List[str]]] = None


class Executor:
    def __init__(self, dry_run: bool = False, env: Optional[Dict[str, str]] = None):
        self.dry_run = dry_run
        self.env = env

    def execute(self, cmd: str):
        """
        >>> e = Executor(dry_run=True, env=dict(user='x'))
        >>> e.execute("qwe $user")
        qwe x
        >>>
        """
        env = self.env or {}

        if self.dry_run:

            for key, val in env.items():
                cmd = cmd.replace("$%s" % key, val)

            print(cmd)

        else:
            subprocess.call(cmd, shell=True, env=env)


def is_seq(a, b, c):
    """
    >>> is_seq(Time(10), Time(12), Time(14))
    True
    >>> is_seq(Time(23), Time(1), Time(4))
    True
    >>> is_seq(Time(10), Time(1), Time(00))
    False
    """
    if a < c:
        return a <= b < c
    else:
        return a <= b or b < c


def str2time(s: str) -> Time:
    return Time(*map(int, s.strip().split(":")))


@dataclass
class ParsedArgs:
    log_level: str
    config: Config
    dry_run: bool
    now: Datetime


def parse(args: dict):
    log_level = args["--log-level"] or DEFAULT_LOG_LEVEL
    config_path = args["--config"] or DEFAULT_CONFIG_PATH
    dry_run = args["--dry-run"]

    with open(config_path) as config:
        config = Config(**yaml.safe_load(config.read()))

    now = Datetime.now()

    if args["--time"]:
        time = str2time(args["--time"])
        now = now.replace(hour=time.hour, minute=time.minute)

    if args["--datetime"]:
        now = Datetime.strptime(args["--datetime"], config.date_fmt)

    return ParsedArgs(
        log_level=log_level,
        config=config,
        dry_run=dry_run,
        now=now,
    )


def smartlock(now, config, executor):
    if config.disable_periods:
        for start, end in config.disable_periods:
            start = Datetime.strptime(start, config.date_fmt)
            end = Datetime.strptime(end, config.date_fmt)
            assert start < end
            if is_seq(start, now, end):
                logging.info("DISABLED")
                return

    if is_seq(str2time(config.safe_time), now.time(), str2time(config.danger_time)):
        logging.info("SAFE")
        executor.execute(config.restore_admin_rights)

    elif is_seq(str2time(config.danger_time), now.time(), str2time(config.critical_time)):
        logging.info("DANGER")
        executor.execute(config.remove_admin_rights)

    else:
        logging.info("CRITICAL")
        executor.execute(config.terminate)


def main():
    args = parse(args=docopt(
        __doc__
        .replace("DEFAULT_CONFIG_PATH", DEFAULT_CONFIG_PATH)
        .replace("DEFAULT_LOG_LEVEL", DEFAULT_LOG_LEVEL)
    ))

    logging.basicConfig(level=getattr(logging, args.log_level), format=DEFAULT_LOG_FORMAT)
    logging.debug(args)

    executor = Executor(dry_run=args.dry_run, env=args.config.env)
    smartlock(args.now, args.config, executor)


if __name__ == "__main__":
    main()
