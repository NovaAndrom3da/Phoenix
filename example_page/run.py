import sys
sys.path.append("/home/runner/Phoenix")
import phoenix
phoenix.config['port'] = 80
phoenix.config['host'] = True
phoenix.config['dumpCache'] = True
phoenix.run(phoenix.config)