# Create virtual env

python3.11.10 -m venv .env

windows: .env\Script\activate

linux: source .env/bin/activate

# install requirements

pip install -r requirements.txt

# Configure CIC Flow Meter

cd cicflowmeter

poetry install

# Run Server

python manage.py runserver

# Manual CIC Flow Meter Testing

cicflowmeter -i "WiFi 2" -u http://localhost:8000/post_flow
