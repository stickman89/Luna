#!/usr/bin/sh

echo 1 > /sys/class/graphics/fb0/blank
echo 1 > /sys/class/graphics/fb1/blank
echo "rm default" > /sys/class/vfm/map
echo "add default vdec.$2.00 amvideo" > /sys/class/vfm/map

python reset_hid.py