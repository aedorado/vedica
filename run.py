"""
Vedica – entry point.
Runs on port 5001 (legacy analytics stays on 5000).
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='127.0.0.1')
