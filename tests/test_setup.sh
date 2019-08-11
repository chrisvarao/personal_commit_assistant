#!/bin/sh

while [ ! -f /keys/test1 ]; do
    sleep 1
done

eval "$(ssh-agent -s)"

ssh-add /keys/test1
ssh-add /keys/test2
mkdir -p ~/.ssh
ssh-keyscan git > ~/.ssh/known_hosts

python3 /tests/test.py

tail -f /dev/null
