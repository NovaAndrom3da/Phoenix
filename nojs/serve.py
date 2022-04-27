# Get NoJS files
from . import nojsbuild as build
import nopm

# Get required assets
from flask import Flask, Response, session, request
from waitress import serve as WSGI_SERVER
import click, random, os, json, gzip, urllib, zlib, sys, time, math


# Configuration
config = { # Set default config settings
  "port": 8080,
  "host": False,
  "canrebuild": False,
  "indexDirectories": False,
  "indexNoJS": False,
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
  "cache-max-age": 31536000
}

if os.path.exists("nojs.config.json") and os.path.isfile("nojs.config.json"):
  configfile = open("nojs.config.json")
  configcont = json.loads(configfile.read())
  configfile.close()
  for i in configcont.keys():
    config[i] = configcont[i]


# Initate run function
class NoJSServer(Flask):
  def run(self, host=False, port=8080):
    return WSGI_SERVER(self, host=['localhost', '0.0.0.0'][host], port=port, ident="NoJS")


# Extensions
extensions = {}

def loadextensions():
  nopm.init()
  ext_list = os.listdir("nojs_files/extensions")
  for ext in ext_list:
    exec(f"import nojs_files.extensions.{ext} as func_ext_{ext}")
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
        print(f"[Prehost] Compressing {url} (mode: zlib, gzip)...")
      if type(cont) == str:
        cont = cont.encode(config["encoding"])
      cont = gzip.compress(zlib.compress(cont))
    elif config["zlib"]:
      if config["verbose"]:
        print(f"[Prehost] Compressing {url} (mode: zlib)...")
      if type(cont) == str:
        cont = cont.encode(config["encoding"])
      cont = zlib.compress(cont)
    elif config["gzip"]:
      if config["verbose"]:
        print(f"[Prehost] Compressing {url} (mode: gzip)...")
      if type(cont) == str:
        cont = cont.encode(config["encoding"])
      cont = gzip.compress(cont)
  else:
    if config["verbose"]:
      print(f"[Prehost] Skipping compression for {url}")
  
  ret = Response(cont, status=200, mimetype=cache[url]["mime"])
  ret.headers["Content-Length"] = len(cont)
  ret.headers["Cache-Control"] = config["cache-max-age"]

  if not url in config["nocompress"]:
    if config["zlib"] and config["gzip"]:
      ret.headers["Content-Encoding"] = 'deflate, gzip'
      if config["verbose"]:
        print(f"[Prehost] Done compressing {url} (mode: zlib, gzip)")
    elif config["zlib"]:
      ret.headers["Content-Encoding"] = 'deflate'
      if config["verbose"]:
        print(f"[Prehost] Done compressing {url} (mode: zlib)")
    elif config["gzip"]:
      ret.headers["Content-Encoding"] = 'gzip'
      if config["verbose"]:
        print(f"[Prehost] Done comrpessing {url} (mode: gzip)")

  
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
        return "[Proxy] Invalid method supplied"
    except Exception as e:
      err = f"[Proxy] [Error] {str(e)}"
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
        return "[Proxy] Invalid method supplied"
    except Exception as e:
      err = f"[Proxy] [Error] {str(e)}"
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

def run(host=config["host"], port=config["port"], indexDirectories=config["indexDirectories"], rebuild=config["canrebuild"]):
  print("[Init] Building server...")
  build_time_start = time.time()
  loadextensions()
  cache = build.build(indexDirectories, config, extensions=extensions)
  
  print("[Init] Done. Initializing server...")
  app = NoJSServer(__name__)
  app.secret_key = os.urandom(16)
  if rebuild:
    @app.route("/nojs/rebuild")
    def nojs_rebuild(): # to be fixed
      if config["verbose"]:
        print("[Rebuild] Starting rebuild.")
      view_funcs = []
      cache = build.build(indexDirectories, config, extensions=extensions)
      for f in cache.keys():
        assign(app, f, cache, view_funcs)
      if config["verbose"]:
        print("[Rebuild] Rebuild finished.")
      view_funcs = []
      for f in cache.keys():
        assign(app, f, cache, view_funcs)
      if config["purgecache"]:
        print("[Clean] Clearing cache")
        del(cache)
        print("[Clean] Done clearing cache")
      return "[Rebuild] Rebuild finished."

  view_funcs = []
  for f in cache.keys():
    assign(app, f, cache, view_funcs)

  for proxy_route in config["proxy"].keys():
    assign_proxy(app, proxy_route, config["proxy"][proxy_route], cache, view_funcs)

  for ext in extensions:
    try:
      extensions[ext].run(app, config, cache)
    except Exception as e:
      print(f"[Error] Issue running extension {ext} in run phase: {str(e)}")
  
  if config["purgecache"]:
    print("[Clean] Clearing cache")
    del(cache)
    print("[Clean] Done clearing cache")
  
  print(f"[Init] Done. Starting server on port {port}...")
  print(f"[Info] Finished in {(time.time()-build_time_start) * 1000} ms")
  try:
    app.run(host, port)
  except KeyboardInterrupt:
    print("[Stop] Terminated by user")
  except Exception as kill_err:
    print(f"[Stop] {kill_err}")


if __name__ == "__main__":
  run()