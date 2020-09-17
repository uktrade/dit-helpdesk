from time import time


class Timer:

    def __init__(self):
        self.start_time = None
        self.stop_time = None

    def start(self):
        self.start_time = time()

    def stop(self):
        self.stop_time = time()

    def elapsed(self):
        if not (self.start_time and self.stop_time):
            return 0.

        return self.stop_time - self.start_time
