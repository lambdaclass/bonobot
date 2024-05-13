#!/usr/bin/env bash

# Make script print every command that is being ran
set -ex

# Change directory to bot's
cd /home/dev/bonobot

# Update codebase
git pull origin master

# Remove old container, build and run the new (updated) on.
docker compose down
docker compose build
docker compose up -d
