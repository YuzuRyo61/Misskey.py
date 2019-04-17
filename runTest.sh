#!/bin/bash
cd $(dirname $0)
coverage run --source=Misskey --omit='venv/*' test/UNIT.py
coverage html --directory=test/coverage