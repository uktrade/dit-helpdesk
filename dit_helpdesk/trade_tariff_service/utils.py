import os


def createDir(path):
    os.makedirs(path, exist_ok=True)
