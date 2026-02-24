import time
import datetime as dt
from PySide6.QtCore import QThread, Signal


class TimerService(QThread):
    # This signal carries the 'now' timestamp to the Window
    heartbeat = Signal(dt.datetime)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.last_date_sent = None

    def run(self):
        while self.running:
            now = dt.datetime.now().replace(microsecond=0)
            self.last_date_sent = now.date()

            # 1. Emit the pulse to the UI
            self.heartbeat.emit(now)

            # 2. Your '5-minute boundary' logic
            next_minute = (now.minute // 5 + 1) * 5
            next_time = now.replace(minute=next_minute % 60, second=0, microsecond=0)

            if next_minute >= 60:
                next_time += dt.timedelta(hours=1)

            sleep_seconds = (next_time - dt.datetime.now()).total_seconds()

            # Safety check: if sleep_seconds is negative (clock drift),
            # sleep for 1 second and try again.
            if sleep_seconds < 0:
                time.sleep(1)
            else:
                time.sleep(sleep_seconds)

    def stop(self):
        self.running = False
