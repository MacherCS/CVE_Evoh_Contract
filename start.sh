#!/bin/bash

npm install

#start ganache as blockchain
nohup ganache-cli -d -i "5777" -p 8546 &

sleep 3s

#run the poc script
node ./poc.js
