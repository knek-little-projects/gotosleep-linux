#!/usr/bin/env python3
import datetime
import os


def hhmm(dt):
    return "%02d:%02d" % (dt.hour, dt.minute)


def is_seq(a, b, c):
    if a < c:
        return a <= b < c
    else:
        return a <= b or b < c


now = hhmm(datetime.datetime.now())


def is_dinner():
    for t in map(int, "10 12 14 16 18 20".split()):
        if is_seq("%02d:00" % t, now, "%02d:10" % t):
            return True


def is_safe():
    return is_seq("05:00", now, "18:00")


def is_danger():
    return is_seq("18:00", now, "23:00")


def is_critical():
    return not is_safe() and not is_danger()


def disable_sudo():
    os.system("""pkill -KILL '^su$'""")
    os.system("""pkill -KILL '^sudo$'""")
    os.system("""test -f /etc/sudoers.d/x && unlink /etc/sudoers.d/x""")


def enable_sudo():
    os.system("""grep -q x /etc/sudoers.d/x || echo 'x ALL=(ALL:ALL) NOPASSWD:ALL' > /etc/sudoers.d/x""")


def screen_lock_root():
    user = "root"
    for display in 0, 1, 2:
      os.system("""pgrep -u%s slock || DISPLAY=:%d sudo -u%s slock""" % (user, display, user))


def screen_unlock_root():
    user = "root"
    os.system("""pgrep -u%s slock && kill -KILL $(pgrep -u%s slock)""" % (user, user))


def killux():
    os.system("""pkill -KILL -ux""")


if is_safe():
    print("SAFE")
    enable_sudo()

    if is_dinner():
        print("DINNER")
        screen_lock_root()
    else:
        print("NO DINNER")
        screen_unlock_root()

elif is_danger():
    print("DANGER")
    disable_sudo()

    if is_dinner():
        print("DINNER")
        screen_lock_root()
    else:
        print("NO DINNER")
        screen_unlock_root()

elif is_critical():
    print("CRITICAL")
    killux()
