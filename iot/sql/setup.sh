# Using tmp101's on the hwmon interface

# To log every 15 minutes add to crontab via crontab -e
*/15 * * * * cd /home/debian/exercises/iot/sql && ./log_tmp101.py >> tmp101_cron.log 2>&1

BUS=i2c-1

config-pin P9_24 i2c
config-pin P9_26 i2c

# Need to set write permissions for group gpio

I2CPATH=/sys/class/i2c-adapter/$BUS

sudo chgrp gpio $I2CPATH/*
sudo chmod g+rw $I2CPATH/*

# Now create the device nodes
echo tmp101 0x49 > $I2CPATH/new_device
echo tmp101 0x4a > $I2CPATH/new_device

dmesg -H | tail -4

# Test the sensors 

cat /sys/class/hwmon/hwmon*/temp1_input
