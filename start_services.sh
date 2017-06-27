#!/bin/bash
bash ./stop_services.sh
echo "Starting node http-server"
http-server &
echo "Starting mosquitto broker"
mosquitto &
echo "Restarting mongodb service"
service mongodb start &



