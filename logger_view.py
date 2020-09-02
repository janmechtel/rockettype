from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import stats

def init_app():
    return QApplication([])

def init_interface():
    window = QWidget()
    status = QLabel('Running & Recording keypresses')

    statstr = get_wpm_by_day()
    wpm = QLabel(statstr)

    layout = QVBoxLayout()
    layout.addWidget(status)
    layout.addWidget(wpm)

    window.setLayout(layout)

    return (status, wpm, window)

def get_wpm_by_day():
    statstr = str(stats.get_stats())
    statstr = "\n".join(statstr.split("\n")[1:-1])
    return "WPM by day:\n" + statstr

def init_systray():
    tray = QSystemTrayIcon(QIcon("icon.ico"))
    menu = QMenu()
    pauseAction = menu.addAction("Toggle Recording")
    statsAction = menu.addAction("See statistics")
    exitAction = menu.addAction("Exit")
    tray.setContextMenu(menu)
    tray.show()

    return (statsAction, pauseAction, exitAction, tray)