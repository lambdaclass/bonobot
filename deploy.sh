#!/usr/bin/env bash

set -ex

# Change directory to bot's
cd /root/bonobot

# Update codebase
git pull

# Search for any containers created with "bot" image and deletes it
make clean

make run SLACK_API_TOKEN=${args[0]} SLACK_BOT_TOKEN=${args[1]}
