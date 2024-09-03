#!/bin/sh


day=`date +%Y%m%d%H%M`
#mv main.log main${day}.log


cd ~/script_new_dev/
/usr/bin/python3 main.py > ./log/main${day}.log

