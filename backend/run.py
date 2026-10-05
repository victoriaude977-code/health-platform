"""Application entry point.

Local development:  python run.py
Production: a WSGI server (gunicorn/waitress) behind nginx - see docs/deploy.md
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Debug mode reloads on file changes - convenient in PyCharm.
    # host 127.0.0.1: the Vite dev server proxies /api here.
    app.run(host="127.0.0.1", port=5000, debug=True)
