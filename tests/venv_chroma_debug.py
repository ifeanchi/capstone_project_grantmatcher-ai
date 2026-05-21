import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print('python:', sys.executable)
try:
    import chromadb
    print('chromadb version:', chromadb.__version__)
    from chromadb.config import Settings
    try:
        client = chromadb.Client(Settings(persist_directory=os.path.abspath('tests/chromadb_persist_test')))
        print('settings client OK')
    except Exception as e:
        print('settings client ERR', type(e).__name__, e)
    try:
        client2 = chromadb.Client()
        print('default client OK')
    except Exception as e:
        print('default client ERR', type(e).__name__, e)
except Exception as e:
    print('import chromadb ERR', type(e).__name__, e)
