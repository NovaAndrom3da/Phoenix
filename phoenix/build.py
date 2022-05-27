from .minify import html_minify, js_minify, css_minify
import os, mimetypes

def readfile(dir, config):
  try:
    f = open(dir)
    data = f.read()
  except UnicodeDecodeError:
    f = open(dir, 'rb')
    data = f.read()
  f.close()
  mime = str(mimetypes.guess_type(dir)[0])
  if config["minify"]:
    try:
      if mime == "text/html":
        data = html_minify(data)
      elif mime == "text/css":
        data = css_minify(data)
      elif mime == "text/js":
        data = js_minify(data)
    except Exception as e:
      print(f"[Error] {str(e)}")

  return {
    "mime": mime,
    "cont": data
  }

def directoryTraverse(dir="./", urldir="/", indexDirectories=False, cache={}, config={}):
  if config["verbose"]:
    print(f"[Build] traversing static directory {dir} ({urldir})")
  index_dir = ""
  dir_ls = os.listdir(dir)
  for f in dir_ls:
    if config["verbose"]:
      print("[Build] reading "+dir+f+" ("+urldir+f+")")
    if os.path.isfile(dir+f):
      cache[urldir+f] = readfile(dir+f, config)
      if indexDirectories:
        index_dir += f"<a href='{urldir+f}'>File: {f}</a><br>"
        if config["verbose"]:
          print(f"[Build] indexed file {dir+f} ({urldir+f})")
    else:
      directoryTraverse(dir+f+"/", urldir+f+"/", indexDirectories, cache, config)
      if os.path.exists(dir+f+"/index.html") and os.path.isfile(dir+f+"/index.html"):
        cache[urldir+f+'/'] = readfile(dir+f+"/index.html", config)
      elif indexDirectories:
        index_dir += f"<a href='{urldir+f}'>Dir: {f}</a><br>"
        if config["verbose"]:
          print("[Build] indexed subdir "+dir+f+" ("+urldir+f+")")
  if indexDirectories:
    cache[urldir] = {"mime": "text/html", "cont": f"<!DOCTYPE html><html><body><h1>Index of {urldir}</h1><div><a href=\"{urldir+'..'}\">Parent Directory</a><br>{index_dir}</div></body></html>"}

def extensionTraverse(dir="./", urldir="/", cache={}, config={}, extensions={}):
  if config["verbose"]:
    print(f"[Build] traversing dynamic directory {dir} ({urldir})")
  dir_ls = os.listdir(dir)
  for f in dir_ls:
    if config["verbose"]:
      print("[Build] reading "+dir+f+" ("+urldir+f+")")
    if os.path.isfile(dir+f):
      for extension in extensions.keys():
        try:
          extensions[extension].srccompile_file(dir+f, urldir+f, cache, readfile, config)
        except AttributeError:
          pass
        except Exception as e:
          print(f"[Error] Error in extension {extension} in srccompile (file: {dir+f}, url: {urldir+f}) phase: '{str(e)}'")
    else:
      extensionTraverse(dir+f+"/", urldir+f+"/", cache, config, extensions)
          
        

def build(indexDirectories=False, config={}, cache={}, extensions={}):
  # ./public/
  if os.path.exists("public"):
    directoryTraverse("public/", "/", indexDirectories, cache, config)

  # ./src/
  if os.path.exists("src"):
    extensionTraverse("src/", "/src/", cache, config, extensions)

  # ./phoenix/
  if os.path.exists("phoenix_files"):
    directoryTraverse("phoenix_files/modules/", "/phoenix/modules/", config["indexPhoenix"], cache, config)

  # ./index.html
  if os.path.exists("index.html") and os.path.isfile("index.html"):
    index = open("index.html")
    cache["/"] = {
      "mime": "text/html",
      "cont": index.read()
    }
    index.close()
  elif not indexDirectories:
    cache["/"] = {
      "mime": "text/html",
      "cont": "<!DOCTYPE html>\n<html><head></head><body></body></html>"
    }

  for ext in extensions.keys():
    try:
      extensions[ext].postbuild(cache)
    except Exception as e:
      print(f"[Error] Error in extension {ext} in postbuild phase: '{str(e)}'")

  return cache
