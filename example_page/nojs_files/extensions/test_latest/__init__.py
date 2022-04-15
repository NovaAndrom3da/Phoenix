print("start defining configurations")
def srccompile_file(dir="./", urldir="/", cache={}, readfile=None): # srccompile step. happens in directory traversal in ./src/
  print(urldir)
  cache[urldir] = {
    "mime": "text/html",
    "cont": "Here is some test stuff"
  }

def postbuild(cache={}): # postbuild step. happens after directory traversal
  for i in cache.keys():
    pass #print(i)

print("end defining configurations")