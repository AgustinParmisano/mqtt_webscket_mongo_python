#!/bin/bash
echo "Stopping Mosquitto Broker"
killall mosquitto
echo "Stopping Node http-server"
killall node
echo "Restarting mongodb service"
service mongodb restart
echo "Done"
exit 0
