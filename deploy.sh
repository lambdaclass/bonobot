#!/usr/bin/env bash

set -ex

# Change directory to bot's
cd /root/bonobot

# Update codebase
git pull

# Remove old container, build and run the new (updated) on.
make run SLACK_API_TOKEN=$1 SLACK_BOT_TOKEN=$2
