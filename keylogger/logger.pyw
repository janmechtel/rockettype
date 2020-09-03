#!python3.8
# https://pynsist.readthedocs.io/en/latest/cfgfile.html#application-section
import sys, os, time
import logging
import site
import ctypes, ctypes.wintypes
from threading import Lock

from pynput import keyboard # pip install pynput
from win10toast import ToastNotifier # pip install win10toast

from keylogger.logger_stats import get_stats
from keylogger.logger_view import *
from keylogger.logger_model import *

# Stores all global variables for the keylogger, such as logging file, debug mode, and keyboard interfaces
env = {}
env_lock = Lock()

def get_active_process():
    active = ctypes.windll.user32.GetForegroundWindow()
    active_window = ctypes.windll.user32.GetWindowThreadProcessId(active,ctypes.byref(env['pid']))

    hProcess = env['OpenProcess'](env['PROCESS_QUERY_INFORMATION'], False, env['pid'])
    if hProcess:
        ImageFileName = (ctypes.c_char*env['MAX_PATH'])()
        if env['GetProcessImageFileName'](hProcess, ImageFileName, env['MAX_PATH'])>0:
            filename = os.path.basename(ImageFileName.value)
        env['CloseHandle'](hProcess)
    return filename.decode('UTF-8')

def __init__():
    # TODO: Store all this stuff in an object
    # taken from https://pynsist.readthedocs.io/en/latest/_modules/nsist.html
    scriptdir, script = os.path.split(__file__)
    installdir = scriptdir  # for compatibility with commands
    pkgdir = os.path.join(scriptdir, 'pkgs')
    # Ensure .pth files in pkgdir are handled properly
    site.addsitedir(pkgdir)
    sys.path.insert(0, pkgdir)

    Psapi = ctypes.WinDLL('Psapi.dll')
    env['GetProcessImageFileName'] = Psapi.GetProcessImageFileNameA
    env['GetProcessImageFileName.restype'] = ctypes.wintypes.DWORD

    Kernel32 = ctypes.WinDLL('kernel32.dll')
    env['OpenProcess'] = Kernel32.OpenProcess
    env['OpenProcess.restype'] = ctypes.wintypes.HANDLE
    env['CloseHandle'] = Kernel32.CloseHandle

    env['pid'] = ctypes.wintypes.DWORD()
    env['MAX_PATH'] = 260
    env['PROCESS_QUERY_INFORMATION'] = 0x0400
    env['previous_time'] = time.time()

    env['log_dir'] = "outputs/"

    # Create an outputs directory if one does not already exist
    try:
        os.mkdir(env['log_dir'])
    except:
        pass

    # Create file w/ header if non existant
    if not os.path.exists(env['log_dir'] + "key_log.txt"):
        with open(env['log_dir'] + "key_log.txt", "w+") as new_file:
            new_file.write("time delta key application\n")

    env['debug_mode'] = os.path.exists(env['log_dir'] + "/DEBUG")

    # Open a file for logging
    env['output_file'] = open(env['log_dir'] + 'key_log.txt', 'a+')
    logging.basicConfig(filename=(env['log_dir'] + "exceptions.txt"), level=logging.DEBUG, format='%(message)s')

    env['should_log'] = True
    env['toaster'] = ToastNotifier()
    env['icon_file'] = data_file_path = os.path.join(os.path.dirname(__file__), 'icon.ico')



def on_press(key):
    # keybinds that always should be dealt with should go up here

    # control-alt-x exits the program. Add GUI for this later
    if str(key) == "<88>": # ctrl-alt-x
        return False

    # control-alt-t prints statistics and sends a notification with statistics too
    if str(key) == "<84>": # ctrl-alt-t
        current_stats = logger_stats.get_stats()

        print(current_stats)

        try:
            env['toaster'].show_toast(f"RocketType Statistics",
                str(current_stats),
                env['icon_file'], duration=7, threaded=True)
        except:
            pass
        return True

    # control-alt-r toggles logging
    if str(key) == "<82>": # ctrl-alt-r
        env['should_log'] = not env['should_log'] # Inverse should_log
        enabled_string = "Enabled" if env['should_log'] else "Disabled"

        # Show notification
        try:
            env['toaster'].show_toast(f"RocketType {enabled_string}",
                " ",
                icon_path=env['icon_file'], duration=3, threaded=True)
        except:
            pass

        time.sleep(1)

        return True # Don't continue to the rest of the function

    if not env['should_log']:
        return True

    # keybinds that should be ignored when recording is off go here

    # SUGGESTION: Ignore keys that are longer than one character long that aren't space (ex: alt)

    current_time = time.time()
    delta = int((current_time - env['previous_time'])*1000)
    process = get_active_process()

    key = key if env['debug_mode'] else "'hidden'" # Only log actual key strokes for debugging as of now

    name = "{current_time} {delta} {key} {process}".format(current_time=current_time,delta=delta,key=str(key), process=process)
    filename = env['log_dir'] + name + ".jpg"

    # Only log name to file if there are 4 columns. Otherwise it will break the stats tool if an error occurs
    if len(name.split(" ")) == 4:
        env['output_file'].write(name + '\n')

    print(name)

    env['previous_time'] = current_time

def async_on_press(key):
    # Locks the env object so that other classes do not try and write / read
    # from it while on_press is using it
    env_lock.acquire()
    ret = True # So that if on_press fails, we still are able to return something
    try:
        ret = on_press(key)
    except Exception as e:
        logging.info(e)

    env_lock.release()
    return ret

def start_keylogger():

    with keyboard.Listener(on_press=async_on_press) as listener:
        env_lock.acquire()
        try:
            env['toaster'].show_toast("RocketType Started and Enabled",
                " ",
                icon_path=env['icon_file'], duration=3, threaded=False)
        except:
            pass
        env_lock.release()
        listener.join()

def main():
    __init__()
    keylogger = logger_thread()
    keylogger.set_func(start_keylogger)

    print(env['icon_file'])

    app = gui(keylogger, env, env_lock)
    app.exec_()

    env['output_file'].close()

    try:
        env['toaster'].show_toast("Exited",
             "RocketType was closed and will not record keystrokes.",
             icon_path=env['icon_file'], duration=5, threaded=False)
    except:
        pass

if __name__ == '__main__':
    main()