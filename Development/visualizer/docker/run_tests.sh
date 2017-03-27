#!/bin/bash

cd /app
source venv/bin/activate
PATH=/app/node_modules/.bin:$PATH
python manage.py test --settings visualizer.test_settings
npm test | tap-xunit > junit/js-test.xml