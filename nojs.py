import nojsbuild as build
import nopm

from flask import Flask, Response
from waitress import serve as WSGI_SERVER
import click

class NoJSServer(Flask):
  def run(self, host=False, port=8080):
    return WSGI_SERVER(self, host=['localhost', '0.0.0.0'][host], port=port)

server_route_functions = {}

def assign(app, url="/", ret="", view_funcs=[]):
  server_route_functions[url] = lambda : ret
  server_route_functions[url].__name__ = f"server_route_func_{url.replace('/', '_').replace('.', '_')}"
  server_route_functions[url].__qualname__ = f"server_route_func_{url.replace('/', '_').replace('.', '_')}"
  view_funcs.append(app.route(url)(server_route_functions[url]))
    
def run(host=False, port=8080, indexDirectories=False):
  print("Building server...")
  cache = build.build(indexDirectories)
  
  print("Done. Initializing server...")
  app = NoJSServer(__name__)
  view_funcs = []
  for f in cache.keys():
    assign(app, f, Response(cache[f]["cont"], status=200, mimetype=cache[f]["mime"]), view_funcs)

  print(f"Done. Starting server on port {port}...")
  app.run(host, port)

@click.command()
@click.option("-h", "--host", "run_host", help="Host the server on a public port", default=False, type=bool)
@click.option("-p", "--port", "run_port", help="Set the port of the server", default=8080, is_flag=True)
def CLICK_host(run_host, run_port):
  print("heehoo")
  run(run_host, run_port)

if __name__ == "__main__":
  run(True, 80, True)