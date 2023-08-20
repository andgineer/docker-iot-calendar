#!/usr/bin/env bash
#
# Pin current dependencies versions.
#

rm -f requirements.txt
rm -f requirements.docker.txt
rm -f requirements.dev.txt

pip-compile requirements.dev.in
pip-compile requirements.docker.in
pip-compile requirements.in
