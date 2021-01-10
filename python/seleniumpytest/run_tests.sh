#!/bin/bash 

cd ${WORKSPACE}/monsrud

# disable python caching
export PYTHONDONTWRITEBYTECODE=1

# remove cache files if they exist
find . -name "*.pyc" | xargs rm -f

pytest \
test_login.py \
test_status.py \
--html=report.html

