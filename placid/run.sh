#!/usr/local/bin/bash

set -a
source client/config.env
set +a

username=
password=

if [ "$DEBUG" = "0" ]; then
  read -p "Username > " username
  read -s -p "Password > " password
  python lsdb_login.py $username $password
else
  python lsdb_login.py
fi
read -p "Press any key to exit."
