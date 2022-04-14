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

def directoryTraverse(dir="./", urldir="/", indexDirectories=False, cache={}, verbose=False):
  if verbose:
    print(f"[Build] traversing static directory {dir} ({urldir})")
  index_dir = ""
  dir_ls = os.listdir(dir)
  for f in dir_ls:
    if verbose:
      print("[Build] reading "+dir+f+" ("+urldir+f+")")
    if os.path.isfile(dir+f):
      cache[urldir+f] = readfile(dir+f)
      if indexDirectories:
        index_dir += f"<a href='{urldir+f}'>File: {f}</a><br>"
        if verbose:
          print("[Build] indexed file "+dir+f+" ("+urldir+f+")")
    else:
      directoryTraverse(dir+f+"/", urldir+f+"/", indexDirectories, cache, verbose)
      if os.path.exists(dir+f+"/index.html") and os.path.isfile(dir+f+"/index.html"):
        cont = readfile(dir+f+"/index.html")
      elif indexDirectories:
        index_dir += f"<a href='{urldir+f}'>Dir: {f}</a><br>"
        if verbose:
          print("[Build] indexed subdir "+dir+f+" ("+urldir+f+")")
        cont = f"<!DOCTYPE html><html><body><h1>Index of {urldir}</h1><div>{index_dir}</div></body></html>"
    try: # For directories that neither have an index.html *or* directory indexing
      cache[urldir] = {
        "mime": "text/html",
        "cont": cont
      }
    except:
      pass

def extensionTraverse(dir="./", urldir="/", cache={}, verbose=False, extensions={}):
  if verbose:
    print(f"[Build] traversing dynamic directory {dir} ({urldir})")
  dir_ls = os.listdir(dir)
  for f in dir_ls:
    if verbose:
      print("[Build] reading "+dir+f+" ("+urldir+f+")")
    if os.path.isfile(dir+f):
      for extension in extensions.keys():
        try:
          extensions[extension].srccompile(dir+f, urldir+f, cache, readfile)
        except AttributeError:
          pass
        except Extension as e:
          print(f"[Error] Error in extension {extension} in srccompile (file: {dir+f}, url: {urldir+f}) phase: '{str(e)}'")
    else:
      extensionTraverse(dir+f+"/", urldir+f+"/", cache, verbose, extensions)
          
        

def build(indexDirectories=False, config={}, cache={}, extensions={}):
  # ./public/
  if os.path.exists("public"):
    directoryTraverse("public/", "/", indexDirectories, cache, config["verbose"])

  # ./src/
  if os.path.exists("src"):
    extensionTraverse("src/", "/src/", cache, config["verbose"], extensions)

  # ./nojs/
  if os.path.exists("nojs_files"):
    directoryTraverse("nojs_files/modules/", "/nojs/modules/", False, cache, config["verbose"])

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
      extensions[extension].postbuild(cache)
    except AttributeError:
      pass
    except Exception as e:
      print(f"[Error] Error in extension {extension} in postbuild phase: '{str(e)}'")

  return cache
