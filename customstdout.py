import sys


class CustomStdOut:
    def __init__(self, console_stdout):
        self.console_stdout = console_stdout

    def write(self, s):
        self.console_stdout.write(s)
        self.flush()

    def flush(self):
        self.console_stdout.flush()


def change_original_stdout():
    sys.stdout = CustomStdOut(sys.stdout)
