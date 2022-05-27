def srccompile_file(dir="./", urldir="/", cache={}, readfile=None, config={}): 
  # srccompile step. happens during directory traversal in ./src/
  print("src test "+urldir)
  cache[urldir] = {
    "mime": "text/html",
    "cont": "Here is some test stuff"
  }

def postbuild(cache={}): # postbuild step. happens after directory traversal
  for i in cache.keys():
    pass #print(i)

def run(app, config={}, cache={}):
  print("extension run is working")
  return
