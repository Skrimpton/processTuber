#!/bin/env python3

import subprocess
import threading
import signal
import json

from PyQt5 import QtCore


class WorkerMeta(QtCore.QObject):
    outSignal = QtCore.pyqtSignal(str)
    noTitleSignal = QtCore.pyqtSignal()
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

        myTitle = None

        self.proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            **kwargs
        )

        for line in self.proc.stdout:
            myResult = line.decode()

        try:
            myJson = json.loads(myResult)
            myTitle = myJson.get("title", None)
        except:
            pass

        self.proc = None

        if myTitle != None:
            self.outSignal.emit(myTitle)
        else:
            self.noTitleSignal.emit()

        self.finishedSignal.emit()

        myTitle=None
