

python3 -m venv venv && ./venv/bin/pip install -r requirements.txt

source venv/bin/activate

lsof -ti:5000 | xargs kill -9 2>/dev/null
python3 run.py