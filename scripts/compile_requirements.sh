#!/usr/bin/env bash
#
# Pin current dependencies versions.
#

rm -f requirements.txt
rm -f requirements.docker.txt
rm -f requirements.dev.txt

# The order is important, because of dependencies between files.
pip-compile requirements.docker.in
pip-compile requirements.in
pip-compile requirements.dev.in
