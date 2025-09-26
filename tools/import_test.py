import importlib
import sys
sys.path.insert(0, '.')

modules = [
    'tools.content_analysis_tools',
    'tools.bedrock_tools'
]

for m in modules:
    try:
        mod = importlib.import_module(m)
        print('import ok:', m)
    except Exception as e:
        print('import FAILED:', m)
        import traceback
        traceback.print_exc()
        raise
