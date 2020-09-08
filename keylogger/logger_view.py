from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import keylogger.logger_stats as stats

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
    try:
        statstr = str(stats.get_stats())
    except Exception as e:
        return "Error retrieving stats: \n" + str(e) + \
            "\nif this issue persists, please consider" + \
            "\ndeleting your key_log.txt file..."
    try:
        statstr = "\n".join(statstr.split("\n")[1:-1])
        return "WPM by day:\n" + statstr
    except:
        return "No data yet"

def init_systray(env):
    tray = QSystemTrayIcon(QIcon(env['icon_file']))
    menu = QMenu()
    pauseAction = menu.addAction("Toggle Recording")
    statsAction = menu.addAction("See statistics")
    exitAction = menu.addAction("Exit")
    tray.setContextMenu(menu)
    tray.show()

    return (statsAction, pauseAction, exitAction, tray)
