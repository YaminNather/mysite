#!/bin/bash
pip install -r requirements.txt
export FLASK_APP=app.py
export FLASK_ENV=production
flask run
