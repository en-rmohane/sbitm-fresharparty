import sys
import os

# Inject the repository root into python path so 'app' and 'config' can be imported
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import create_app

# Vercel Serverless Function entry point
app = create_app()

if __name__ == '__main__':
    app.run()

