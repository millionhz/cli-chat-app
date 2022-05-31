#!/bin/bash

for i in {1..20}
do
   echo "Test $i"
   python3 TestChatApp.py | grep Failed

   echo "Sleeping for 5 sec"
   sleep 5
done