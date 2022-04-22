__URL__ = "https://nojs-repo.vercel.app"

import os, urllib.request, tarfile, tempfile, shutil

def init():
  pathgen = ["nojs_files", "nojs_files/modules", "nojs_files/extensions"]
  for path in pathgen:  
    if not os.path.exists(path):
      os.mkdir(path)
  filegen = ["nojs.package.json"]
  for file in filegen:
    if not os.path.exists(file):
      open(file, 'w').close()
      

def niceurl(string=""):
  return string.replace("/", "_").replace("-", "_")

def install_module(pkg="", version="latest", repourl=__URL__):
  if not os.path.exists(f"nojs_files/modules/{pkg}"):
    version_out = version
    if version == "latest":
      version = urllib.request.urlopen(f'{repourl}/modules/{niceurl(pkg)}/latest.txt').read().decode()
    response = urllib.request.urlopen(f"{repourl}/modules/{niceurl(pkg)}/{niceurl(version)}.tar.xz")
    status = response.getcode()

    tar = tarfile.open(pkg+".tar.xz", mode="r|xz", fileobj=response)
    tar.extractall(f"nojs_files/modules/{niceurl(pkg)}_{version_out}")
    tar.close()
    return True
  print(f"[Okay] '{pkg}' is already installed")
  
def install_extension(pkg="", version="latest", repourl=__URL__):
  if not os.path.exists(f"nojs_files/extensions/{pkg}.js"):
    version_out = version
    if version == "latest":
      version = urllib.request.urlopen(f'{repourl}/extensions/{niceurl(pkg)}/latest.txt').read().decode()
    response = urllib.request.urlopen(f"{repourl}/extensions/{niceurl(pkg)}/{niceurl(version)}.tar.xz")
    status = response.getcode()

    tar = tarfile.open(pkg+".tar.xz", mode="r|xz", fileobj=response)
    tar.extractall(f"nojs_files/extensions/{niceurl(pkg)}_{version_out}")
    tar.close()
    return True
  print(f"[Okay] '{pkg}' is already installed")
  
def install(pkg="", version="latest", type="*", repourl=__URL__): # version to be implemented
  init()
  pkg = pkg.strip().lstrip()
  type = type.lower()
  try:
    if type == "*":
      try:
        if install_module(pkg, version, repourl): return
      except:
        if install_extension(pkg, version, repourl): return
    elif type == "module" or type == "mod" or type == "m":
      install_module(pkg, version, repourl)
    elif type == "extension" or type == "ext" or type == "e":
      install_extension(pkg, version, repourl)
    
    print(f"[Okay] '{pkg}' installed sucessfully")

  except Exception as e:
    print(f"[Error] '{pkg}' install returned '{str(e)}'")

def remove_module(pkg=""):
  if os.path.exists(f"nojs_files/modules/{pkg}"):
    shutil.rmtree(f"nojs_files/modules/{pkg}")
    print(f"[Okay] Module '{pkg}' removed sucessfully")
    return True
  else:
    print(f"[Okay] Module '{pkg}' is not installed")

def remove_extension(pkg=""):
  if os.path.exists(f"nojs_files/extensions/{pkg}"):
    shutil.rmtree(f"nojs_files/extensions/{pkg}")
    print(f"[Okay] Extension '{pkg}' removed sucessfully")
    return True
  else:
    print(f"[Okay] Extension '{pkg}' is not installed")

def remove(pkg="", type="*"):
  init()
  pkg = pkg.strip().lstrip()

  if type == "*":
    if remove_module(pkg): return
    if remove_extension(pkg): return
  elif type == "module" or type == "mod" or type == "m":
    remove_module(pkg)
  elif type == "extension" or type == "ext" or type == "e":
    remove_extension(pkg)