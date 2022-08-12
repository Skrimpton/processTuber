import subprocess
import threading
import signal

from PyQt5 import QtCore


class Worker(QtCore.QObject):
    outSignal = QtCore.pyqtSignal(str)
    finishedSignal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()
        self.thread_is_running = threading.Event()
        self.proc = None

    def run_command(self, cmd, **kwargs):
        threading.Thread(
            target=self._execute_command,
            args=(cmd,),
            kwargs=kwargs,
            daemon=True
        ).start()

    def _execute_command(self, cmd, **kwargs):

        self.proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            **kwargs
        )


        for line in self.proc.stdout:

            if self.stop_event.isSet():
                self.outSignal.emit("!!! TERMINATED !!!")
                self.proc.terminate()
                self.proc = None
                self.stop_event.clear()
                return

            self.outSignal.emit(line.decode())

        self.proc = None
        self.outSignal.emit("All Done :)")
        self.finishedSignal.emit()
