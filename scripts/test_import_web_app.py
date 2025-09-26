import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    import web.app as app
    print('web.app import OK')
except Exception as e:
    print('web.app import FAILED:', e)
    raise
