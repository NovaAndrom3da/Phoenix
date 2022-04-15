# Get NoJS files
from . import nojsbuild as build
import nopm

# Get required assets
from flask import Flask, Response, session
from waitress import serve as WSGI_SERVER
import click, random, os, json, gzip

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
  "gzip": True,
  "gzip_dynamic_pages": False, # is always false if gzip is false
  "gzip_encoding": "utf-8",
  "args": {}
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
  
  if !("args" in cache[url]): cache[url]["args"] = [] # autoupgrade to blank arguments
  if cache[url]["args"] == [] or type(cont) != str:
    # Gzip Compress
    if config["gzip"]:
      if config["verbose"]:
        print(f"[Build] Compressing {url}...")
      if type(cont) == str:
        cont = cont.encode(config["gzip_encoding"])
      cont = gzip.compress(cont)


    ret = Response(cont, status=200, mimetype=cache[url]["mime"])


    if config["gzip"]:
      ret.headers["Content-Encoding"] = 'gzip'
      ret.headers["Content-length"] = len(cont)
      if config["verbose"]:
        print(f"[Build] Done comrpessing {url}")

  
    server_route_functions[url] = lambda : ret
    name = f"server_route_func_{url.replace('/', '_').replace('.', '_')}_{random.randint(0, 10000000)}"
    server_route_functions[url].__name__ = name
    server_route_functions[url].__qualname__ = name
    view_funcs.append(app.route(url)(server_route_functions[url]))
  else:
    session_args = []
    if type(config["args"] != dict):
      print(f"[Warn] Static variables are of wrong type ('{type(config['args']}') not 'dict'")
      config["args"] = {}
    for arg in cache[url]["args"]:
      if arg.startswith("session:"):
        session_args.append(arg.lstrip("session:"))
      else:
        if !(arg in config["args"]):
          print(f"[Warn] Unassigned static variable '{arg}'")
          config["args"][arg] = ""
        cache[url["cont"] = cont.replace("${{"+arg+"}}", config["args"][arg])
    if len(session_args) == 0:
      assign(app, url, cache, view_funcs)
      return

    dynamic_arg_page = None
    if config["gzip"] and config["gzip_dynamic_pages"]:
      print(f"[Note] gzip is enabled for dynamic page '{url}'. This may take more time to compute")
      def dynamic_arg_page():
        for arg in session_args:
          if !(arg in session.keys()):
            print(f"[Warn] Session argument '{arg}' not in session keys")
          else:
            cont = cont.replace("${{session:"+arg+"}}", session[arg])
        cont = gzip.compress(cont.encode(config["gzip_encoding"]))
        ret = Response(cont, status=200, mimetype=cache[url]["mime"])
        ret.headers["Content-Encoding"] = 'gzip'
        ret.headers["Content-length"] = len(cont)
        return ret
    else:
      def dynamic_arg_page():
        for arg in session_args:
          if !(arg in session.keys()):
            print(f"[Warn] Session argument '{arg}' not in session keys")
          else:
            cont = cont.replace("${{session:"+arg+"}}", session[arg])
          ret = Response(cont, status=200, mimetype=cache[url]["mime"])
          return ret
    server_route_functions[url] = dynamic_arg_page
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

  print(f"[Init] Done. Starting server on port {port}...")
  app.run(host, port)

if __name__ == "__main__":
  run()