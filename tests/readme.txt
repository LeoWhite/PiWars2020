Generating the .dtbo file 

dtc -@ -I dts -O dtb -o tb2.dtbo tb2.dts
sudo cp tb2.dtbo /boot/overlays/

vi /boot/config.txt
idtoverlay=tb2

