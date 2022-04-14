__URL__ = "https://nojs-repo.vercel.app"

import os, urllib.request

def init():
  if not os.path.exists("nojs"):
    os.mkdir("nojs")
    os.mkdir("nojs/modules")
    #os.mkdir("nojs/extensions") # maybe add extensions at one point

def install(pkg="", version="latest"): # version to be implemented
  init()
  pkg = pkg.strip().lstrip()
  if not os.path.exists(f"nojs/modules/{pkg}.js"):
    try:
      response = urllib.request.urlopen(f"{__URL__}/modules/{pkg}.js")
      status = response.getcode()
    
      file = open(f"nojs/modules/{pkg}.js", "w")
      file.write(response.read().decode())
      file.close()
    
      if status != 200:
        print(f"[Warn] The server responded with a non-200 status '{status}'")

      print(f"[Okay] '{pkg}' installed sucessfully")

    except Exception as e:
      print(f"[Error] '{pkg}' install returned '{str(e)}'")
  else:
    print(f"[Okay] '{pkg}' is already installed")

def remove(pkg=""):
  init()
  pkg = pkg.strip().lstrip()

  if os.path.exists(f"nojs/modules/{pkg}.js"):
    os.rm
  else:
    print("[Error] '{pkg}' was not found")