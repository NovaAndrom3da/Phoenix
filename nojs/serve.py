# Get NoJS files
from . import nojsbuild as build
import nopm

# Get required assets
from flask import Flask, Response, session
from waitress import serve as WSGI_SERVER
import click, random, os, json, gzip, urllib.request, zlib

# Initate run function
class NoJSServer(Flask):
  def run(self, host=False, port=8080):
    return WSGI_SERVER(self, host=['localhost', '0.0.0.0'][host], port=port)


# Configuration
config = { # Set default config settings
  "proxy": [],
  "port": 8080,
  "host": False,
  "canrebuild": False,
  "indexDirectories": False,
  "verbose": False,
  "zlib": True,
  "gzip": True,
  "encoding": "utf-8",
  "nocompress": [],
  "purgecache": True
}

if os.path.exists("nojs.config.json") and os.path.isfile("nojs.config.json"):
  configfile = open("nojs.config.json")
  configcont = json.loads(configfile.read())
  configfile.close()
  for i in configcont.keys():
    config[i] = configcont[i]


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
        cont = cont.encode(config["enoding"])
      cont = gzip.compress(cont)
  else:
    if config["verbose"]:
      print(f"[Prehost] Skipping compression for {url}")
  
  ret = Response(cont, status=200, mimetype=cache[url]["mime"])
  ret.headers["Content-Length"] = len(cont)

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
  view_funcs.append(app.route(url)(server_route_functions[url]))   

  
def run(host=config["host"], port=config["port"], indexDirectories=config["indexDirectories"], rebuild=config["canrebuild"]):
  print("[Init] Building server...")
  loadextensions()
  cache = build.build(indexDirectories, config, extensions=extensions)
  
  print("[Init] Done. Initializing server...")
  app = NoJSServer(__name__)
  app.secret_key = os.urandom(16)
  if rebuild:
    @app.route("/nojs/rebuild")
    def nojs_rebuild(): # to be fixed
      cache = build.build(indexDirectories)
      view_funcs = []
      for f in cache.keys():
        assign(app, f, cache, view_funcs)
      return "[Note] Rebuild completed."

  view_funcs = []
  for f in cache.keys():
    assign(app, f, cache, view_funcs)

  if config["purgecache"]:
    print("[Clean] Clearing cache")
    del(cache)
    print("[Clean] Done clearing cache")
  
  print(f"[Init] Done. Starting server on port {port}...")
  app.run(host, port)

if __name__ == "__main__":
  run()