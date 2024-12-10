# Project Setup Guide

## Create Virtual Environment

```sh
python3.11.10 -m venv .env
```

### Activate Virtual Environment

- **Windows**:
  ```sh
  .env\Scripts\activate
  ```
- **Linux**:
  ```sh
  source .env/bin/activate
  ```

## Install Requirements

```sh
pip install -r requirements.txt
```

## Configure CIC Flow Meter

```sh
cd cicflowmeter
poetry install
```

## Database Migrations

### Make Migrations

```sh
python manage.py makemigrations
```

### Apply Migrations

```sh
python manage.py migrate
```

## Run Server

```sh
python manage.py runserver
```

## Manual CIC Flow Meter Testing

```sh
cicflowmeter -i "WiFi 2" -u http://localhost:8000/post_flow
```
