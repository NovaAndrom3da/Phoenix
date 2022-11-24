VERSION = "2.0.0.3"

# Get Phoenix files
from . import build
from ppm import PPM

# Get required assets
from flask import Flask, Response, request #,  session
from waitress import serve as WSGI_SERVER
import random, os, json, gzip, urllib, zlib, time, types #, math, sys



# Configuration
config = {                    # Set default config settings
  "port": 8080,               # Port to host on
  "host": False,              # Enable connections from other IP addresses
  # "canrebuild": False,        # Enable rebuilding of Phoenix server
  "indexDirectories": False,  # Enable directory indexing
  "indexPhoenix": False,      # Enable indexing of the phoenix_files directory
  "verbose": False,           # Enable verbose output
  "zlib": True,               # Enable zlib compression
  "gzip": True,               # Enable gzip compression
  "encoding": "utf-8",        # Encoding to use
  "nocompress": [],           # List of URLs to not compress
  "minify": True,             # Enable minification of HTML
  "proxy": {},                # Proxy settings
  "fixProxy": True,           # Fix URLs in proxied content to point to the proxy
  "thisURL": None,            # URL to use for proxying
  "cache-max-age": 259200,    # Cache max age (3 days)
  "threads": 4,               # Number of threads to use
  "dumpCache": False          # Dump cache to file
}

fore = {
  "Error": "\033[31m",        # Red
  "Info": "\033[94m",         # Blue
  "Init": "\033[94m",         # Blue
  "Stop": "\033[33m",         # Yellow
  "Prehost": "\033[92m",      # Green
  "Proxy": "\033[34m",        # Cyan
  "Clean": "\033[35m",        # Magenta

  "reset": "\033[39m"         # Reset the color
}

def info_out(type='Info'):
  # Get type of output and auto-format it
  s = ''
  e = ''
  if type in fore:
    s = fore[type]
    e = fore['reset']
  return f"[ {s}{type}{e} ]"

# Check if the configuration file exists
if os.path.exists("config.phoenix") and os.path.isfile("config.phoenix"):
  configfile = open("config.phoenix")
  configcont = json.loads(configfile.read())
  configfile.close()
  for i in configcont.keys():
    config[i] = configcont[i]

max_cpu_threads = os.cpu_count()
if 'sched_getaffinity' in os.__dir__():
  # Adjust number of threads to use based on the number of CPU cores
  max_cpu_threads = len(os.sched_getaffinity(0))
else:
  # If the sched_getaffinity function is not available, it could be because of an incompatible OS
  print(f"{info_out('Info')} The host system does not support fetching the amount of usable cores")
if config['verbose'] and config['threads'] < max_cpu_threads:
  # Print a notice that the program is not using the max number of threads available
  print(f"{info_out('Info')} The server is running on {config['threads']} thread(s), while there are {max_cpu_threads} available.")

if config['threads'] > max_cpu_threads:
  # Print a warning if the number of threads is less than the number of CPU cores
  print(f"{info_out('Error')} The server was configured to run on {config['threads']} thread(s), when there are only {max_cpu_threads} available. Switching to maximum.")

  # Reset the number of used threads to the maximum available
  config['threads'] = max_cpu_threads

if config['threads'] <= 0:
  # Print an error if the number of threads is less than or equal to 0
  print(f"{info_out('Error')} The specified number of threads, {config['threads']}, is less than zero. Setting threads to 1")

  # Reset the number of used threads to 1
  config['threads'] = 1
  
# Initate run function
class PhoenixServer(Flask):
  # Create PhoenixServer class for Waitress backend server
  def run(self, host=False, port=8080, threads=4):
    return WSGI_SERVER(self, host=['localhost', '0.0.0.0'][host], port=port, ident="Phoenix", threads=threads)


# Extensions
extensions = {}

# Load the extensions in the extensions directory
def loadextensions():
  # Initialize the package manager
  PPM.init()
  # List the extensions in the extensions directory
  ext_list = os.listdir("phoenix_files/extensions")
  # Iterate through the extensions
  for ext in ext_list:
    # TODO: Test if the exec() function can be used to exploit a vulnerability
    #       in the server. If it can, use the importlib module instead.
    #       Although, the extensions can already run python code, so it's not
    #       a huge deal if it can run arbitrary code based on the folder's name.
    # Run the extension's __init__.py file
    exec(f"import phoenix_files.extensions.{ext} as func_ext_{ext}")

    # Add the extension to the loaded extensions list
    exec(f"extensions['{ext}'] = func_ext_{ext}")


# Dynamic route
server_route_functions = {}

def assign(app, url="/", cache={}, view_funcs=[]):
  # Get content from each file in the cache
  cont = cache[url]["cont"]

  # Gzip Compress
  # Check if the file has compression disabled
  if not url in config["nocompress"]:
    # Check if the file uses both forms of compression, zlib and gzip
    if config["zlib"] and config["gzip"]:
      if config["verbose"]:
        print(f"{info_out('Prehost')} Compressing {url} (mode: zlib, gzip)...")

      # Encode the file's content into binary
      if type(cont) == str:
        cont = cont.encode(config["encoding"])

      # Compress the binary encoded content
      cont = gzip.compress(zlib.compress(cont))
    elif config["zlib"]:
      if config["verbose"]:
        print(f"{info_out('Prehost')} Compressing {url} (mode: zlib)...")

      # Encode the file's content into binary
      if type(cont) == str:
        cont = cont.encode(config["encoding"])

      # Compress the binary encoded content
      cont = zlib.compress(cont)
    elif config["gzip"]:
      if config["verbose"]:
        print(f"{info_out('Prehost')} Compressing {url} (mode: gzip)...")

      # Encode the file's content into binary
      if type(cont) == str:
        cont = cont.encode(config["encoding"])

      # Compress the binary encoded content
      cont = gzip.compress(cont)
  else:
    if config["verbose"]:
      print(f"{info_out('Prehost')} Skipping compression for {url}")

  # Create responses for each file
  ret = Response(cont, status=200, mimetype=cache[url]["mime"])
  # Add the max-age header to the response
  ret.headers["Cache-Control"] = f"max-age={config['cache-max-age']}"

  # Check agian if the file has compression disabled
  # Perhaps incorporate the above code into this one
  if not url in config["nocompress"]:
    if config["zlib"] and config["gzip"]:
      # Set the content length and encoding headers
      ret.headers["Content-Length"] = len(cont)
      ret.headers["Content-Encoding"] = 'deflate, gzip'

      if config["verbose"]:
        print(f"{info_out('Prehost')} Done compressing {url} (mode: zlib, gzip)")
    elif config["zlib"]:
      # Set the content length and encoding headers
      ret.headers["Content-Length"] = len(cont)
      ret.headers["Content-Encoding"] = 'deflate'

      if config["verbose"]:
        print(f"{info_out('Prehost')} Done compressing {url} (mode: zlib)")
    elif config["gzip"]:
      # Set the content length and encoding headers
      ret.headers["Content-Length"] = len(cont)
      ret.headers["Content-Encoding"] = 'gzip'

      if config["verbose"]:
        print(f"{info_out('Prehost')} Done comrpessing {url} (mode: gzip)")

  # Add the response to the view functions list using a lambda function
  server_route_functions[url] = lambda : ret
  # Give the lambda function a name so it doesn't complain
  name = f"server_route_func_{url.replace('/', '_').replace('.', '_')}_{random.randint(0, 10000000)}"
  server_route_functions[url].__name__ = name
  server_route_functions[url].__qualname__ = name

  # Set the view function for the file in the cache
  # TODO: Add a way to change the view function for a file in
  #       the cache without having to restart the server
  cache[url]["view_func"] = len(view_funcs)

  # Apply the lambda function to the url and add it to the view functions list
  view_funcs.append(app.route(url)(server_route_functions[url]))   

# Create the proxy
def assign_proxy(app, url="/", proxy="localhost:3000", cache={}, view_funcs=[]):
  # Proxy any requests to the root directory of the specified URL
  def server_proxy_index():
    try:
      if request.method == "GET":
        # Proxy the GET request to the specified url and read the response
        cont = urllib.request.urlopen(proxy).read()

        # Check if fixProxy is enabled and replace URLs in the response with the proxy URL
        if type(cont) == str and config["thisURL"] != None and config["fixProxy"]:
          cont = cont.replace(proxy, config["thisURL"]+url)

        # Return the response from the proxy
        return cont
      elif request.method == "POST":
        # Proxy the POST request to the specified url and read the response
        cont = urllib.request.urlopen(urllib.request.Request(proxy, urllib.parse.urlencode(request.form).encode()))

        # Check if fixProxy is enabled and replace URLs in the response with the proxy URL
        if type(cont) == str and config["thisURL"] != None and config["fixProxy"]:
          cont = cont.replace(proxy, config["thisURL"]+url)

        # Return the response from the proxy
        return cont
      else:
        # Return an error if the request method is not GET or POST
        return f"{info_out('Proxy')} Invalid method supplied"
    except Exception as e:
      # Return an error if the proxy fails
      err = f"{info_out('Proxy')} {info_out('Error')} {str(e)}"

      if config["verbose"]:
        print(err)

      return err

  # Proxy any requests to a subdirectory of the specified URL
  def server_proxy_subpath(suburl):
    try:
      if request.method == "GET":
        # Proxy the GET request to the specified url and read the response
        cont = urllib.request.urlopen(f"{proxy}/{suburl}").read()

        # Check if fixProxy is enabled and replace URLs in the response with the proxy URL
        if type(cont) == str and config["thisURL"] != None and config["fixProxy"]:
          cont = cont.replace(proxy, config["thisURL"]+url)

        # Return the response from the proxy
        return cont
      elif request.method == "POST":
        # Proxy the POST request to the specified url and read the response
        cont = urllib.request.urlopen(urllib.request.Request(f"{proxy}/{suburl}", urllib.parse.urlencode(request.form).encode()))

        # Check if fixProxy is enabled and replace URLs in the response with the proxy URL
        if type(cont) == str and config["thisURL"] != None and config["fixProxy"]:
          cont = cont.replace(proxy, config["thisURL"]+url)

        # Return the response from the proxy
        return cont
      else:
        # Return an error if the request method is not GET or POST
        return f"{info_out('Proxy')} Invalid method supplied"
    except Exception as e:
      # Return an error if the proxy fails
      err = f"{info_out('Proxy')} {info_out('Error')} {str(e)}"

      if config["verbose"]:
        print(err)

      return err

  # Give the lambda proxy functions a name so they don't complain
  name_index = f"server_route_func_proxy_index_{url.replace('/', '_').replace('.', '_')}_{random.randint(0, 10000000)}"
  server_proxy_index.__name__ = name_index
  server_proxy_index.__qualname__ = name_index

  name_subpath = f"server_route_func_proxy_path_{url.replace('/', '_').replace('.', '_')}_{random.randint(0, 10000000)}"
  server_proxy_subpath.__name__ = name_subpath
  server_proxy_subpath.__qualname__ = name_subpath

  # Add the proxy functions to the view functions list
  view_funcs.append(app.route(url, methods=["POST", "GET"])(server_proxy_index))
  view_funcs.append(app.route(f"{url}/<path:suburl>", methods=["POST", "GET"])(server_proxy_subpath))




# Get a readable version of the cache
def cacheTree(cache, i, path):
  # Recurse through the cache if the item is a dictionary
  if type(i) == dict:
    for ib in i.keys():
      cacheTree(cache, i[ib], f"{path}^?{ib}")

  # Return '<bytes>' if the item is a bytes object
  elif type(i) == bytes:
    i = '<bytes>'

  # Return '<function>' if the item is a function
  elif type(i) == types.FunctionType:
    i = '<function>'

  # Convert other objects into strings
  else:
    i = str(i)

  # To be honest, I don't know what this does
  it = cache

  for p in path.split('^?')[:-1]:
    it = cache[p]

  it[path.split('^?')[-1]] = i

# Put the readable version of the cache into an output file
def dumpCache(cache={}):
  # Open the output file
  cache_file_out = open('phoenix_files/cache.json', 'w')

  # Get the readable version of the cache
  for i in cache.copy().keys():
    cacheTree(cache, cache[i], i)

  # Convert the readable version to JSON and write it to the file
  cache_file_out.write(json.dumps(cache))
  cache_file_out.close()

  print(f"{info_out('Info')} Dumped cache to phoenix_files/cache.json")



# The main run function
def run(config=config):
  # Get the configuration
  host = config['host']
  port = config['port']
  indexDirectories = config['indexDirectories']
  # rebuild = config['canrebuild']
  
  print(f"{info_out('Init')} Building server...")

  # Get the time the server started
  build_time_start = time.time()

  # Load the extensions
  loadextensions()

  # Create the cache
  cache = build.build(indexDirectories, config, extensions=extensions)
  
  print(f"{info_out('Init')} Done. Initializing server...")

  # Create the Flask app
  app = PhoenixServer(__name__)

  # Add a secret key to the app
  app.secret_key = os.urandom(16)

  # TODO: Add a way to rebuild the server without restarting it
  # if rebuild:
  #   @app.route("/Phoenix/rebuild")
  #   def Phoenix_rebuild(): # to be fixed
  #     if config["verbose"]:
  #       print(f"{info_out('Rebuild')} Starting rebuild.")
  #     view_funcs = []
  #     cache = build.build(indexDirectories, config, extensions=extensions)
  #     for f in cache.keys():
  #       assign(app, f, cache, view_funcs)
  #     if config["verbose"]:
  #       print(f"{info_out('Rebuild')} Rebuild finished.")
  #     view_funcs = []
  #     for f in cache.keys():
  #       assign(app, f, cache, view_funcs)
  #     return f"{info_out('Rebuild')} Rebuild finished."

  # Assign the routes to the app
  view_funcs = []
  for f in cache.keys():
    assign(app, f, cache, view_funcs)

  for proxy_route in config["proxy"].keys():
    assign_proxy(app, proxy_route, config["proxy"][proxy_route], cache, view_funcs)

  # Run the extensions
  for ext in extensions:
    try:
      extensions[ext].run(app, config, cache)
    except Exception as e:
      print(f"{info_out('Error')} Issue running extension {ext} in run phase: {str(e)}")

  # Dump the cache to a file if the config says to
  if config["dumpCache"]:
    dumpCache(cache)
  
  print(f"{info_out('Init')} Done. Starting server on port {port}...")

  # Print the time it took the server to start
  print(f"{info_out('Info')} Finished in {(time.time()-build_time_start) * 1000} ms")

  try:
    # Try to start the server
    app.run(host, port, config['threads'])
  except KeyboardInterrupt:
    # Exit the server if the user presses Ctrl+C
    print(f"{info_out('Stop')} Terminated by user")
  except Exception as kill_err:
    # Print an error if the server fails to start
    print(f"{info_out('Stop')} {info_out('Error')} {kill_err}")


# if __name__ == "__main__":
#   run()
