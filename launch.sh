#!/bin/bash

if [ -d "hootbot" ] 
then
    source hootbot/bin/activate
else
    git submodule update --init 
    curl "https://bootstrap.pypa.io/get-pip.py" --output get-pip.py
    python3 get-pip.py
    python3 -m pip install -U virtualenv
    virtualenv hootbot
    source hootbot/bin/activate
    python3 -m pip install -r requirements.txt
fi

if [[ "$1" == "-b" ]]
then
    python3 bot.py
else
    python3 start.py
fi
