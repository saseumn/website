#!/bin/bash

# Exit if any errors occur.
set -e

# Variables
WORKERS=1 # TODO: Calculate this based on server.
HOST=0.0.0.0
PORT=7400 # Configured on the server.

# Enter virtual environment.
rm -rf .virtualenv
virtualenv -p python3 .virtualenv
source .virtualenv/bin/activate

# Install dependencies.
pip install -r requirements.txt

# Run gunicorn.
gunicorn -w $WORKERS -b "$HOST:$PORT" "main:make_app()" &
