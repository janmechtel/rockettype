#!python3.8
# https://pynsist.readthedocs.io/en/latest/cfgfile.html#application-section
import sys, os
import site

# taken from https://pynsist.readthedocs.io/en/latest/_modules/nsist.html
scriptdir, script = os.path.split(__file__)
installdir = scriptdir  # for compatibility with commands
pkgdir = os.path.join(scriptdir, 'pkgs')
# Ensure .pth files in pkgdir are handled properly
site.addsitedir(pkgdir)
sys.path.insert(0, pkgdir)

import time

import logging
import os
import ctypes, ctypes.wintypes

from pynput import keyboard # pip install pynput
from win10toast import ToastNotifier # pip install win10toast

import stats

Psapi = ctypes.WinDLL('Psapi.dll')
GetProcessImageFileName = Psapi.GetProcessImageFileNameA
GetProcessImageFileName.restype = ctypes.wintypes.DWORD

Kernel32 = ctypes.WinDLL('kernel32.dll')
OpenProcess = Kernel32.OpenProcess
OpenProcess.restype = ctypes.wintypes.HANDLE
CloseHandle = Kernel32.CloseHandle

pid = ctypes.wintypes.DWORD()
MAX_PATH = 260
PROCESS_QUERY_INFORMATION = 0x0400

def get_active_process():
    active = ctypes.windll.user32.GetForegroundWindow()
    active_window = ctypes.windll.user32.GetWindowThreadProcessId(active,ctypes.byref(pid))

    hProcess = OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
    if hProcess:
        ImageFileName = (ctypes.c_char*MAX_PATH)()
        if GetProcessImageFileName(hProcess, ImageFileName, MAX_PATH)>0:
            filename = os.path.basename(ImageFileName.value)
        CloseHandle(hProcess)
    return filename.decode('UTF-8')


previous_time = time.time()

log_dir = "outputs/"

# Create an outputs directory if one does not already exist
try:
    os.mkdir(log_dir)
except:
    pass

# Create file w/ header if non existant
if not os.path.exists(log_dir + "key_log.txt"):
    with open(log_dir + "key_log.txt", "w+") as new_file:
        new_file.write("time delta key application\n")

debug_mode = os.path.exists(log_dir + "/DEBUG")

logging.basicConfig(filename=(log_dir + "key_log.txt"), level=logging.DEBUG, format='%(message)s')

should_log = True
toaster = ToastNotifier()

def on_press(key):
    global should_log
    global toaster

    # keybinds that always should be dealt with should go up here

    # control-alt-x exits the program. Add GUI for this later
    if str(key) == "<88>": # ctrl-alt-x
        return False

    # control-alt-t prints statistics and sends a notification with statistics too
    if str(key) == "<84>": # ctrl-alt-t
        current_stats = stats.get_stats()

        print(current_stats)

        toaster.show_toast(f"RocketType Statistics",
            str(current_stats),
            icon_path="icon.ico", duration=7, threaded=True)
        return True

    # control-alt-r toggles logging
    if str(key) == "<82>": # ctrl-alt-r
        should_log = not should_log # Inverse should_log
        enabled_string = "Enabled" if should_log else "Disabled"

        # Show notification
        toaster.show_toast(f"RocketType {enabled_string}",
            " ",
            icon_path="icon.ico", duration=3, threaded=True)

        return True # Don't continue to the rest of the function

    if not should_log:
        return True

    # keybinds that should be ignored when recording is off go here

    # SUGGESTION: Ignore keys that are longer than one character long that aren't space (ex: alt)

    global previous_time
    current_time = time.time()
    delta = int((current_time - previous_time)*1000)
    process = get_active_process()

    key = key if debug_mode else "'hidden'" # Only log actual key strokes for debugging as of now

    name = "{current_time} {delta} {key} {process}".format(current_time=current_time,delta=delta,key=str(key), process=process)
    filename = log_dir + name + ".jpg"

    # Only log name to file if there are 4 columns. Otherwise it will break the stats tool if an error occurs
    if len(name.split(" ")) == 4:
        logging.info(name)

    print(name)

    previous_time = current_time

with keyboard.Listener(on_press=on_press) as listener:
    toaster.show_toast("RocketType Started and Enabled",
        " ",
        icon_path="icon.ico", duration=3, threaded=True)
    listener.join()

toaster.show_toast("Exited",
     "RocketType was closed and will not record keystrokes.",
     icon_path="icon.ico", duration=5, threaded=True)
