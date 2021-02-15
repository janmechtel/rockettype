#!python3.8
# https://pynsist.readthedocs.io/en/latest/cfgfile.html#application-section
import sys, os, time, signal
import logging
import site
import csv
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

    env['log_dir'] = "Logs/"
    env['keyboard'] = keyboard.Controller()
    env['typos'] = init_typos()

    
    # Create an outputs directory if one does not already exist
    try:
        os.mkdir(env['log_dir'])
    except:
        pass

    env['debug_mode'] = os.path.exists(env['log_dir'] + "/DEBUG")

    # Create file w/ header if non existant
    if not os.path.exists(env['log_dir'] + "key_log.txt"):
        with open(env['log_dir'] + "key_log.txt", "w+") as new_file:
            new_file.write("time delta key application\n")

    # Open a file for logging
    env['output_file'] = open(env['log_dir'] + 'key_log.txt', 'a+')
    logging.basicConfig(level=logging.DEBUG, format='%(message)s',
        handlers=[logging.FileHandler(env['log_dir'] + "exceptions.txt"),
        logging.StreamHandler()])

    env['should_log'] = True
    env['toaster'] = ToastNotifier()
    env['icon_file'] = data_file_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    env['words'] = [""]

def init_typos():
    typos = {}
    with open('commonTypos.csv', newline='') as csvfile:
        typoread = csv.reader(csvfile, delimiter=':', quotechar='|')
        for row in typoread:
            typos[row[2]] = row[4]

    print(f"Number of typos read from .csv: {len(typos)}")
    
    return typos

def on_press(key):
    # keybinds that always should be dealt with should go up here

    # control-alt-x exits the program. Add GUI for this later
    if str(key) == "<88>": # ctrl-alt-x
        return False

    # control-alt-t prints statistics and sends a notification with statistics too
    if str(key) == "<84>": # ctrl-alt-t
        env['show_window']()

        time.sleep(1)
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


    current_time = time.time()
    delta = int((current_time - env['previous_time'])*1000)
    process = get_active_process()

    key = key if env['debug_mode'] else "'hidden'" # Only log actual key strokes for debugging as of now

    name = "{current_time} {delta} {key} {process}".format(current_time=current_time,delta=delta,key=str(key), process=process)
    filename = env['log_dir'] + name + ".jpg"

    # Only log name to file if there are 4 columns. Otherwise it will break the stats tool if an error occurs
    if len(name.split(" ")) == 4:
        env['output_file'].write(name + '\n')

    # print(name)
    
    # SUGGESTION: Ignore keys that are longer than onddmaybe whesould mot go back so cuhe character long that aren't space (ex: alt)
    if key == keyboard.Key.space:
        completedWord = env['words'][-1]
        print(completedWord)
        if completedWord in env['typos']:
            print("TYPO detected " + completedWord)
            print(env['typos'][completedWord])

            for _ in range(0, len(completedWord)+1):
                env['keyboard'].press(keyboard.Key.backspace)
                env['keyboard'].release(keyboard.Key.backspace)
            env['keyboard'].type(env['typos'][completedWord]+" ")
            
        if completedWord == "teh":
            print("ERROR detected - sending the opposite keys")
            env['keyboard'].press(keyboard.Key.backspace)
            env['keyboard'].release(keyboard.Key.backspace)
            env['keyboard'].press(keyboard.Key.backspace)
            env['keyboard'].release(keyboard.Key.backspace)
            env['keyboard'].press(keyboard.Key.backspace)
            env['keyboard'].release(keyboard.Key.backspace)
        env['words'].append("")    

    if len(str(key)) <= 3:
        env['words'][-1]  = env['words'][-1] + str(key).replace("'","")
        env['words']=env['words'][-5:] 

    print(env['words'][-1], end="\r")
    env['previous_time'] = current_time

def async_on_press(key):
    # Locks the env object so that other classes do not try and write / read
    # from it while on_press is using it
    env_lock.acquire()
    ret = True # So that if on_press fails, we still are able to return something
    try:
        ret = on_press(key)
    except Exception as e: 
        print(e)
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

def keylogger_locker():
    '''Prevents more than one instance of RocketType from running at the
    same time. Will return false if another instance detected.'''
    
    # In Debug mode, always delete LOCK fils
    if env['debug_mode']:
        os.remove(env['log_dir'] + "LOCK")

    if not os.path.exists(env['log_dir'] + "LOCK"):
        open(env['log_dir'] + "LOCK", "w+").close()
        return True
    else:
        logging.error("logfile detected, will exit now. Consider to delete: " + env['log_dir'] + "LOCK")
        return False

def reset_lock():
    '''Deletes the lock file'''
    try:
        os.remove(env['log_dir'] + "LOCK")
    except:
        pass

def main():
    __init__()

    if not keylogger_locker():
        env['toaster'].show_toast("Failed to start",
            "It appears that RocketType is already running!",
            icon_path=env['icon_file'], duration=5, threaded=False)
        sys.exit()

    # Remove LOCK file when killed
    signal.signal(signal.SIGINT, reset_lock)
    signal.signal(signal.SIGTERM, reset_lock)
    signal.signal(signal.SIGABRT, reset_lock)

    keylogger = logger_thread()
    keylogger.set_func(start_keylogger)

    app = gui(keylogger, env, env_lock)
    app.exec_()

    env['output_file'].close()

    reset_lock()

    try:
        env['toaster'].show_toast("Exited",
             "RocketType was closed and will not record keystrokes.",
             icon_path=env['icon_file'], duration=5, threaded=False)
    except:
        pass

if __name__ == '__main__':
    main()
