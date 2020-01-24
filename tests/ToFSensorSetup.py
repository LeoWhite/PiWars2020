sleep 0.25
gpio -g write 9 1
/home/pi/vl53l1x-python/examples/change-address.py --current 0x29 --desired 0x20

sleep 0.25
gpio -g write 7 1
/home/pi/vl53l1x-python/examples/change-address.py --current 0x29 --desired 0x21

sleep 0.25
gpio -g write 8 1
/home/pi/vl53l1x-python/examples/change-address.py --current 0x29 --desired 0x30

gpio -g write 10 1
/home/pi/vl53l1x-python/examples/change-address.py --current 0x29 --desired 0x31
