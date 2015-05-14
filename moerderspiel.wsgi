
import logging, sys
sys.path.insert(0, '/home/da/public_html/moerder-dev')
sys.stdout = sys.stderr
logging.basicConfig(stream=sys.stderr)

from moerderspiel import app as application
