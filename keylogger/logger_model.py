from PyQt5.QtCore import *
import keylogger.logger_view as logger_view

class gui:
    def __init__(self, logger_thread, env, env_lock):
        self.app = logger_view.init_app()
        self.app.setQuitOnLastWindowClosed(False) # Keep open with tray icon


        # Should be the objects themselves, not copies, therefore editing will
        # change the original
        self.env = env
        self.env_lock = env_lock

        # Items for (re)displaying and changing window elements
        if_bp = logger_view.init_interface()
        self.status = if_bp[0]
        self.wpm = if_bp[1]
        self.window = if_bp[2]

        self.env_lock.acquire() # Uses icon file, so wait until safe to do so
        # Items for showing the system tray and controlling buttons
        st_bp = logger_view.init_systray(env)
        self.show = st_bp[0]
        self.pause = st_bp[1]
        self.exit = st_bp[2]
        self.tray = st_bp[3] # This is to prevent the garbage collector from deleting it
        self.env_lock.release()

        self.pause.triggered.connect(self.pause_app)
        self.exit.triggered.connect(self.app.exit)
        self.show.triggered.connect(self.show_window)

        self.env['show_window'] = self.show.trigger

        self.logger = logger_thread

        self.logger.finished.connect(self.app.exit)
        self.logger.start()

        # self.show_window(None)

    def show_window(self, q):
        self.wpm.setText(logger_view.get_wpm_by_day())
        self.env_lock.acquire()
        # TODO: Update this when window is open and should_log changes,
        # either with event or by setting it each time that happens in the code
        status_str = "Enabled" if self.env['should_log'] else "Disabled"
        self.status.setText(status_str)
        self.env_lock.release()

        self.window.show()

    def pause_app(self, q):
        self.env_lock.acquire()
        self.env['should_log'] = not self.env['should_log']
        enabled_string = "Enabled" if self.env['should_log'] else "Disabled"
        # Show notification
        try:
            self.env['toaster'].show_toast(f"RocketType {enabled_string}",
                " ",
                icon_path=self.env['icon_file'], duration=3, threaded=True)
        except:
            pass
        self.env_lock.release()

    def exec_(self):
        self.app.exec_()

class logger_thread(QThread):
    def set_func(self, start_logger):
        self.func = start_logger

    def run(self):
        self.func()
