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

def directoryTraverse(dir="./", urldir="/", indexDirectories=False, cache={}):
  index_dir = ""
  dir_ls = os.listdir(dir)
  for f in dir_ls:
    print("reading "+f)
    if os.path.isfile(dir+f):
      cache[urldir+f] = readfile(dir+f)
      if indexDirectories:
        index_dir += f"<a href='{urldir+f}'>File: {f}</a><br>"
        print("indexed file "+f)
    else:
      directoryTraverse(dir+f+"/", urldir+f+"/", indexDirectories, cache)
      if indexDirectories:
        index_dir += f"<a href='{urldir+f}'>Dir: {f}</a><br>"
        print("indexed subdir "+f)
    cache[urldir] = {
      "mime": "text/html",
      "cont": f"<!DOCTYPE html><html><body><h1>Index of {urldir}</h1><div>{index_dir}</div></body></html>"
    }

def build(indexDirectories=False, cache={}):
  # ./public/
  if os.path.exists("public"):
    directoryTraverse("public/", "/", indexDirectories, cache)
#    root_public = os.listdir("public")
 #   for i in root_public:
  #    print(root_public[i])

  # ./src/
  if os.path.exists("src"):
    directoryTraverse("src/", "/src/", indexDirectories, cache)
#    root_src = os.listdir("src")
 #   for i in root_src:
  #    print(root_src[i])

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
    
  return cache
