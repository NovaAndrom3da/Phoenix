import os

def init():
  if not os.path.exists("nojs"):
    os.mkdir("nojs")
    os.mkdir("nojs/pkgs")
    os.mkdir("nojs/extensions")

def install(pkg=""):
  init()
  