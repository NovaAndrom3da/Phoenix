__URL__ = "https://nojs-repo.vercel.app"

import os, urllib.request, tarfile, shutil, json

def pkg_json_r():
  pkg_json_fr = open("package.phoenix", 'r')
  pkg_json_rr = pkg_json_fr.read()
  pkg_json_fr.close()
  return json.loads(pkg_json_rr)

def pkg_json_dictw(write_dict={}):
  pkg_json_dw = open('package.phoenix', 'w')
  pkg_json_dw.write(json.dumps(write_dict))
  pkg_json_dw.close()

def pkg_json_w(key='', val=''):
  pkg_json_ww = pkg_json_r()
  pkg_json_ww[key] = val
  pkg_json_dictw(json.dumps(pkg_json_ww))

def init():
  pathgen = ["phoenix_files", "phoenix_files/modules", "phoenix_files/extensions"]
  for path in pathgen:  
    if not os.path.exists(path):
      os.mkdir(path)

  if not os.path.exists("package.phoenix"):
    pkg_json_dictw()

  filegen = []
  for file in filegen:
    if not os.path.exists(file):
      open(file, 'w').close()

def niceurl(string=""):
  return string.replace("/", "_").replace("-", "_")

def install_module(pkg="", version="latest", repourl=__URL__):
  if not os.path.exists(f"phoenix_files/modules/{pkg}"):
    version_out = version
    if version == "latest":
      version = urllib.request.urlopen(f'{repourl}/modules/{niceurl(pkg)}/latest.txt').read().decode()
    response = urllib.request.urlopen(f"{repourl}/modules/{niceurl(pkg)}/{niceurl(version)}.tar.xz")
    status = response.getcode()

    tar = tarfile.open(pkg+".tar.xz", mode="r|xz", fileobj=response)
    tar.extractall(f"phoenix_files/modules/{niceurl(pkg)}_{version_out}")
    tar.close()

    pkg_json_w('mod:'+pkg, version)
    
    return True
  print(f"[Okay] '{pkg}' is already installed")
  
def install_extension(pkg="", version="latest", repourl=__URL__):
  if not os.path.exists(f"phoenix_files/extensions/{pkg}.js"):
    version_out = version
    if version == "latest":
      version = urllib.request.urlopen(f'{repourl}/extensions/{niceurl(pkg)}/latest.txt').read().decode()
    response = urllib.request.urlopen(f"{repourl}/extensions/{niceurl(pkg)}/{niceurl(version)}.tar.xz")
    status = response.getcode()

    tar = tarfile.open(pkg+".tar.xz", mode="r|xz", fileobj=response)
    tar.extractall(f"phoenix_files/extensions/{niceurl(pkg)}_{version_out}")
    tar.close()

    pkg_json_w('ext:'+pkg, version)
    
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
  if os.path.exists(f"phoenix_files/modules/{pkg}"):
    shutil.rmtree(f"phoenix_files/modules/{pkg}")
    print(f"[Okay] Module '{pkg}' removed sucessfully")

    pkg_config = pkg_json_r()
    del(pkg_config['mod:'+pkg])
    pkg_json_dictw(pkg_config)
    
    return True
  else:
    print(f"[Okay] Module '{pkg}' is not installed")

def remove_extension(pkg=""):
  if os.path.exists(f"phoenix_files/extensions/{pkg}"):
    shutil.rmtree(f"phoenix_files/extensions/{pkg}")
    print(f"[Okay] Extension '{pkg}' removed sucessfully")

    pkg_config = pkg_json_r()
    del(pkg_config['ext:'+pkg])
    pkg_json_dictw(pkg_config)
    
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

def update(repo=__URL__):
  packages = pkg_json_r()
  for pkg in packages.keys():
    if pkg.startswith('mod:'):
      if packages[pkg] != urllib.request.urlopen(f'{repourl}/extensions/{niceurl(pkg)}/latest.txt').read().decode():
        pkg = pkg[4:]
        remove_module(pkg)
        install_module(pkg, repourl=repo)
        print(f"[Done] Updated module {pkg}.")
    elif pkg.startswith('ext:'):
      if packages[pkg] != urllib.request.urlopen(f'{repo}/extensions/{niceurl(pkg)}/latest.txt').read().decode():
        pkg = pkg[4:]
        remove_extension(pkg)
        install_extension(pkg, repourl=repo)
        print(f"[Done] Updated extension {pkg}.")
    else:
      print(f"[Error] Issue in updating packages: {pkg} is not properly formatted.")