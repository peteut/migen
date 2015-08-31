import subprocess
from contextlib import contextmanager
import os


@contextmanager
def pwd(path):
    cwd = os.getcwd()
    os.chdir(os.path.join(cwd, path))
    yield
    os.chdir(cwd)


def vpi_extension(cmdobj):
    with pwd("vpi"):
        subprocess.check_call(["make"])
