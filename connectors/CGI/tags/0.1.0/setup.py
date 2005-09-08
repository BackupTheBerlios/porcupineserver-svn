# setup.py
"py2exe script for generating executable CGI"
from distutils.core import setup
import py2exe

setup(console=["porcupine.py"], zipfile=None)
