#!/usr/bin/sh

echo 0 > /sys/class/graphics/fb0/blank
echo 0 > /sys/class/graphics/fb1/blank
echo "rm default" > /sys/class/vfm/map
echo "add default decoder ppmgr amlvideo deinterlace amvideo" > /sys/class/vfm/map
python reset_hid.py