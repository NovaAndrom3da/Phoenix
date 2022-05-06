from .serve import run, NoPM, config, loadextensions
import sys, os

if '-p' in sys.argv:
  config['port'] = sys.argv[sys.argv.index('-p')+1]

if '--port' in sys.argv:
  config['port'] = sys.argv[sys.argv.index('--port')+1]

if '--host' in sys.argv:
  config['host'] = True

if 'run' in sys.argv:
  run()

repo = "https://nojs-repo.vercel.app"
if '--repo' in sys.argv:
  repo = sys.argv[sys.argv.index('--repo')+1]

if 'install' in sys.argv:
  to_install = sys.argv[sys.argv.index('install')+1:]
  for pkg in to_install:
    pl = pkg.split("==")
    name = pl[0]
    package_len = len(pl)
    version = 'latest'
    ok = True
    if package_len == 2:
      version = pl[1]
    elif package_len != 1:
      print(f"[Error] Improperly formatted package '{pkg}'")
      ok = False
    if ok:
      NoPM.i(name, version, repourl=repo)

if 'remove' in sys.argv:
  to_remove = sys.argv[sys.argv.index('remove')+1:]
  for pkg in to_remove:
    NoPM.r(pkg)