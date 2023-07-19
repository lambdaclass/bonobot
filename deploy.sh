#!/usr/bin/env bash

set -ex

# Change directory to bot's
cd /root/bonobot

# Update codebase
git pull

make run SLACK_API_TOKEN=$1 SLACK_BOT_TOKEN=$2
