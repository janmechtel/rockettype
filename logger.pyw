import time

import logging
import sys, os
import ctypes, ctypes.wintypes

from pynput import keyboard # pip install pynput
from win10toast import ToastNotifier # pip install win10toast

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

try:
    os.mkdir(log_dir) # Confirm directory existst
    open(log_dir + "key_log.txt", "a+").close() # Confirm file exist
except:
    pass
logging.basicConfig(filename=(log_dir + "key_log.txt"), level=logging.DEBUG, format='%(message)s')

should_log = True
toaster = ToastNotifier()

def on_press(key):
    global should_log
    global toaster

    # control-alt-r toggles logging
    if str(key) == "<82>":
        should_log = not should_log # Inverse should_log
        enabled_string = "Enabled" if should_log else "Disabled"

        enabled_desc = "Rocket type recording typed text"
        disabled_desc = "Text recording paused..."

        # Show notification
        toaster.show_toast(f"Rocket Type {enabled_string}",
             enabled_desc if should_log else disabled_desc,
             icon_path="icon.ico", duration=3, threaded=True)

        return True # Don't continue to the rest of the function

    if not should_log:
        return True

    # control-alt-x exits the program. Add GUI for this later
    if str(key) == "<88>":
        return False

    global previous_time
    current_time = time.time()
    delta = int((current_time - previous_time)*1000)
    process = get_active_process()

    name = "{current_time} {delta} {key} {process}".format(current_time=current_time,delta=delta,key=str(key), process=process)
    filename = log_dir + name + ".jpg"
    logging.info(name)
    print(name)

    previous_time = current_time


with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

toaster.show_toast(f"Rocket Type Exited",
     "Rocket Type has been closed and will no longer record keystrokes",
     icon_path="icon.ico", duration=5, threaded=True)
