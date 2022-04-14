import os, mimetypes

def readfile(dir):
  try:
    f = open(dir)
    data = f.read()
  except UnicodeDecodeError:
    f = open(dir, 'rb')
    data = f.read()
  f.close()
  return {
    "mime": str(mimetypes.guess_type(dir)[0]),
    "cont": data
  }

def directoryTraverse(dir="./", urldir="/", indexDirectories=False, cache={}, verbose=False, extensions=[]):
  index_dir = ""
  dir_ls = os.listdir(dir)
  for f in dir_ls:
    if verbose:
      print("reading "+dir+f+" ("+urldir+f+")")
    if os.path.isfile(dir+f):
      cache[urldir+f] = readfile(dir+f)
      if indexDirectories:
        index_dir += f"<a href='{urldir+f}'>File: {f}</a><br>"
        if verbose:
          print("indexed file "+dir+f+" ("+urldir+f+")")
    else:
      directoryTraverse(dir+f+"/", urldir+f+"/", indexDirectories, cache)
      if os.path.exists(dir+f+"index.html") and os.path.isfile(dir+f+"index.html"):
        pass
      elif indexDirectories:
        index_dir += f"<a href='{urldir+f}'>Dir: {f}</a><br>"
        if verbose:
          print("indexed subdir "+dir+f+" ("+urldir+f+")")
    
    cache[urldir] = {
      "mime": "text/html",
      "cont": f"<!DOCTYPE html><html><body><h1>Index of {urldir}</h1><div>{index_dir}</div></body></html>"
    }

def build(indexDirectories=False, config={}, cache={}, extensions={}):
  # ./public/
  if os.path.exists("public"):
    directoryTraverse("public/", "/", indexDirectories, cache, config["verbose"])

  # ./src/
  if os.path.exists("src"):
    directoryTraverse("src/", "/src/", indexDirectories, cache, config["verbose"])

  # ./nojs/
  if os.path.exists("nojs"):
    directoryTraverse("nojs/", "/nojs/", False, cache, config["verbose"])

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

  for extension in extensions.keys():
    try:
      cache = extension.build(cache)
    except:
      pass
  return cache
