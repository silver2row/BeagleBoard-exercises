# source this file
# Set the API key in the environment variable
export OPENWEATHER_API_KEY=67fa0224b7c49d8b80695211708769
# add ca

BUS=i2c-1
ADDR=0x40
DEV=si7020

echo $DEV $ADDR > /sys/class/i2c-adapter/$BUS/new_device
dmesg -H | tail -2

# Add the cron job
*/5 * * * * /usr/bin/python3 /home/yoder/home/exercises/sensor_logger.py >> /home/yoder/home/exercises/sensor_log.txt 2>&1
