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
            return 0.0

        return self.stop_time - self.start_time


def flatten(list_of_lists):
    return [item for inner_list in list_of_lists for item in inner_list]


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]  # noqa: E203


def unique(iterable):
    seen = set()
    for i in iterable:
        if i in seen:
            continue
        seen.add(i)
        yield i
