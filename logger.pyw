from pynput import keyboard
import cv2
import time

import logging

import sys, os.path, ctypes, ctypes.wintypes

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
    #print (pid)
    #print (active)
    #print (active_window)

    hProcess = OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
    #print(hProcess)
    if hProcess:
        ImageFileName = (ctypes.c_char*MAX_PATH)()
        if GetProcessImageFileName(hProcess, ImageFileName, MAX_PATH)>0:
            filename = os.path.basename(ImageFileName.value)
            #print(filename)
        CloseHandle(hProcess)
    return filename.decode('UTF-8')


previous_time = time.time()
#cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
# if not cap.isOpened():
#     raise IOError("Cannot open webcam")

log_dir = "outputs/"

logging.basicConfig(filename=(log_dir + "key_log.txt"), level=logging.DEBUG, format='%(message)s')


def on_press(key):
    global previous_time
    #ret, frame = cap.read()
    # frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    # TODO how to offload this into something asynchronous, so this is not blocking?
    #frame = cv2.flip(frame,flipCode=-1)
    #frame = cv2.putText(frame, str(key), (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0),2) 
    current_time = time.time()
    delta = int((current_time - previous_time)*1000)
    process = get_active_process()
    
    name = "{current_time} {delta} {key} {process}".format(current_time=current_time,delta=delta,key=str(key), process=process)
    filename = log_dir + name + ".jpg"
    logging.info(name)
    print(name)
    
    # cv2.imwrite(filename,frame)
    previous_time = current_time

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

# cap.release()
# cv2.destroyAllWindows()

