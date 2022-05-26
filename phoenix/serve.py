VERSION = "1.0.4"
# Get Phoenix files
from . import build
from ppm import PPM

# Get required assets
from flask import Flask, Response, session, request
from phoenix_waitress import serve as WSGI_SERVER
import click, random, os, json, gzip, urllib, zlib, sys, time, math

class Fore():
  red = "\033[31m"
  lightblue = "\033[94m"
  yellow = "\033[33m"
  lightgreen = "\033[92m"
  blue = "\033[34m"
  magenta = "\033[35m"

  reset = "\033[39m"

# Configuration
config = { # Set default config settings
  "port": 8080,
  "host": False,
  "canrebuild": False,
  "indexDirectories": False,
  "indexPhoenix": False,
  "verbose": False,
  "zlib": True,
  "gzip": True,
  "encoding": "utf-8",
  "nocompress": [],
  "purgecache": True,
  "minify": True,
  "proxy": {},
  "fixProxy": True,
  "thisURL": None,
  "cache-max-age": 31536000,
  "threads": 4
}

if os.path.exists("Phoenix.config.json") and os.path.isfile("Phoenix.config.json"):
  configfile = open("Phoenix.config.json")
  configcont = json.loads(configfile.read())
  configfile.close()
  for i in configcont.keys():
    config[i] = configcont[i]

max_cpu_threads = len(os.sched_getaffinity(0))
if config['verbose'] and config['threads'] < max_cpu_threads:
  print(f"[{Fore.lightblue} Info {Fore.reset}] The server is running on {config['threads']} thread(s), while there are {max_cpu_threads} available.")

if config['threads'] > max_cpu_threads:
  print(f"[{Fore.red} Error {Fore.reset}] The server was configured to run on {config['threads']} thread(s), when there are only {max_cpu_threads} available. Switching to maximum.")
  config['threads'] = max_cpu_threads

if config['threads'] <= 0:
  print(f"[{Fore.red} Error {Fore.reset}] The specified number of threads, {config['threads']}, is less than zero. Setting threads to 1")
  config['threads'] = 1
  
# Initate run function
class PhoenixServer(Flask):
  def run(self, host=False, port=8080, threads=4):
    return WSGI_SERVER(self, host=['localhost', '0.0.0.0'][host], port=port, ident="Phoenix", threads=threads)


# Extensions
extensions = {}

def loadextensions():
  PPM.init()
  ext_list = os.listdir("phoenix_files/extensions")
  for ext in ext_list:
    exec(f"import phoenix_files.extensions.{ext} as func_ext_{ext}")
    exec(f"extensions['{ext}'] = func_ext_{ext}")


# Dynamic route
server_route_functions = {}

def assign(app, url="/", cache={}, view_funcs=[]):
  # Get content
  cont = cache[url]["cont"]

  # Gzip Compress
  if not url in config["nocompress"]:
    if config["zlib"] and config["gzip"]:
      if config["verbose"]:
        print(f"[{Fore.lightblue} Prehost {Fore.reset}] Compressing {url} (mode: zlib, gzip)...")
      if type(cont) == str:
        cont = cont.encode(config["encoding"])
      cont = gzip.compress(zlib.compress(cont))
    elif config["zlib"]:
      if config["verbose"]:
        print(f"[{Fore.lightblue} Prehost {Fore.reset}] Compressing {url} (mode: zlib)...")
      if type(cont) == str:
        cont = cont.encode(config["encoding"])
      cont = zlib.compress(cont)
    elif config["gzip"]:
      if config["verbose"]:
        print(f"[{Fore.lightblue} Prehost {Fore.reset}] Compressing {url} (mode: gzip)...")
      if type(cont) == str:
        cont = cont.encode(config["encoding"])
      cont = gzip.compress(cont)
  else:
    if config["verbose"]:
      print(f"[{Fore.lightblue} Prehost {Fore.reset}] Skipping compression for {url}")
  
  ret = Response(cont, status=200, mimetype=cache[url]["mime"])
  ret.headers["Cache-Control"] = f"max-age={config['cache-max-age']}"

  if not url in config["nocompress"]:
    if config["zlib"] and config["gzip"]:
      ret.headers["Content-Length"] = len(cont)
      ret.headers["Content-Encoding"] = 'deflate, gzip'
      if config["verbose"]:
        print(f"[{Fore.lightgreen} Prehost {Fore.reset}] Done compressing {url} (mode: zlib, gzip)")
    elif config["zlib"]:
      ret.headers["Content-Length"] = len(cont)
      ret.headers["Content-Encoding"] = 'deflate'
      if config["verbose"]:
        print(f"[{Fore.lightgreen} Prehost {Fore.reset}] Done compressing {url} (mode: zlib)")
    elif config["gzip"]:
      ret.headers["Content-Length"] = len(cont)
      ret.headers["Content-Encoding"] = 'gzip'
      if config["verbose"]:
        print(f"[{Fore.lightgreen} Prehost {Fore.reset}] Done comrpessing {url} (mode: gzip)")

  
  server_route_functions[url] = lambda : ret
  name = f"server_route_func_{url.replace('/', '_').replace('.', '_')}_{random.randint(0, 10000000)}"
  server_route_functions[url].__name__ = name
  server_route_functions[url].__qualname__ = name
  cache[url]["view_func"] = len(view_funcs)
  view_funcs.append(app.route(url)(server_route_functions[url]))   

def assign_proxy(app, url="/", proxy="localhost:3000", cache={}, view_funcs=[]):
  def server_proxy_index():
    try:
      if request.method == "GET":
        cont = urllib.request.urlopen(proxy).read()
        if type(cont) == str and config["thisURL"] != None and config["fixProxy"]:
          cont = cont.replace(proxy, config["thisURL"]+url)
        return cont
      elif request.method == "POST":
        cont = urllib.request.urlopen(urllib.request.Request(proxy, urllib.parse.urlencode(request.form).encode()))
        if type(cont) == str and config["thisURL"] != None and config["fixProxy"]:
          cont = cont.replace(proxy, config["thisURL"]+url)
        return cont
      else:
        return f"[{Fore.blue} Proxy {Fore.reset}] Invalid method supplied"
    except Exception as e:
      err = f"[{Fore.blue} Proxy {Fore.reset}] [{Fore.red} Error {Fore.reset}] {str(e)}"
      if config["verbose"]:
        print(err)
      return err
  
  def server_proxy_subpath(suburl):
    try:
      if request.method == "GET":
        cont = urllib.request.urlopen(f"{proxy}/{suburl}").read()
        if type(cont) == str and config["thisURL"] != None and config["fixProxy"]:
          cont = cont.replace(proxy, config["thisURL"]+url)
        return cont
      elif request.method == "POST":
        cont = urllib.request.urlopen(urllib.request.Request(f"{proxy}/{suburl}", urllib.parse.urlencode(request.form).encode()))
        if type(cont) == str and config["thisURL"] != None and config["fixProxy"]:
          cont = cont.replace(proxy, config["thisURL"]+url)
        return cont
      else:
        return f"[{Fore.blue} Proxy {Fore.reset}] Invalid method supplied"
    except Exception as e:
      err = f"[{Fore.blue} Proxy {Fore.reset}] [{Fore.red} Error {Fore.reset}] {str(e)}"
      if config["verbose"]:
        print(err)
      return err

  name_index = f"server_route_func_proxy_index_{url.replace('/', '_').replace('.', '_')}_{random.randint(0, 10000000)}"
  server_proxy_index.__name__ = name_index
  server_proxy_index.__qualname__ = name_index

  name_subpath = f"server_route_func_proxy_path_{url.replace('/', '_').replace('.', '_')}_{random.randint(0, 10000000)}"
  server_proxy_subpath.__name__ = name_subpath
  server_proxy_subpath.__qualname__ = name_subpath

  view_funcs.append(app.route(url, methods=["POST", "GET"])(server_proxy_index))
  view_funcs.append(app.route(f"{url}/<path:suburl>", methods=["POST", "GET"])(server_proxy_subpath))

def run(config=config):
  host = config['host']
  port = config['port']
  indexDirectories=config['indexDirectories']
  rebuild=config['canrebuild']
  
  print(f"[{Fore.lightblue} Init {Fore.reset}] Building server...")
  build_time_start = time.time()
  loadextensions()
  cache = build.build(indexDirectories, config, extensions=extensions)
  
  print(f"[{Fore.lightblue} Init {Fore.reset}] Done. Initializing server...")
  app = PhoenixServer(__name__)
  app.secret_key = os.urandom(16)
  if rebuild:
    @app.route("/Phoenix/rebuild")
    def Phoenix_rebuild(): # to be fixed
      if config["verbose"]:
        print(f"[{Fore.lightblue} Rebuild {Fore.reset}] Starting rebuild.")
      view_funcs = []
      cache = build.build(indexDirectories, config, extensions=extensions)
      for f in cache.keys():
        assign(app, f, cache, view_funcs)
      if config["verbose"]:
        print(f"[{Fore.magenta} Rebuild {Fore.reset}] Rebuild finished.")
      view_funcs = []
      for f in cache.keys():
        assign(app, f, cache, view_funcs)
      if config["purgecache"]:
        print(f"[{Fore.magenta} Clean {Fore.reset}] Clearing cache")
        del(cache)
        print(f"[{Fore.magenta} Clean {Fore.reset}] Done clearing cache")
      return f"[{Fore.magenta} Rebuild {Fore.reset}] Rebuild finished."

  view_funcs = []
  for f in cache.keys():
    assign(app, f, cache, view_funcs)

  for proxy_route in config["proxy"].keys():
    assign_proxy(app, proxy_route, config["proxy"][proxy_route], cache, view_funcs)

  for ext in extensions:
    try:
      extensions[ext].run(app, config, cache)
    except Exception as e:
      print(f"[ {Fore.red} Error {Fore.reset} ] Issue running extension {ext} in run phase: {str(e)}")
  
  if config["purgecache"]:
    print(f"[{Fore.magenta} Clean {Fore.reset}] Clearing cache")
    del(cache)
    print(f"[{Fore.magenta} Clean {Fore.reset}] Done clearing cache")
  
  print(f"[{Fore.lightblue} Init {Fore.reset}] Done. Starting server on port {port}...")
  print(f"[{Fore.lightblue} Info {Fore.reset}] Finished in {(time.time()-build_time_start) * 1000} ms")
  try:
    app.run(host, port, config['threads'])
  except KeyboardInterrupt:
    print(f"[{Fore.yellow} Stop {Fore.reset}] Terminated by user")
  except Exception as kill_err:
    print(f"[{Fore.red} Stop {Fore.reset}] {kill_err}")


# if __name__ == "__main__":
#   run()