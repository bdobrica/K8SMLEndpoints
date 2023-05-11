#!/bin/bash
cd /opt/app
python3 -m flask --app predict run -h 0.0.0.0 -p 8070 "$@"
