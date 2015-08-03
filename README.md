# weewx_rtl_433
Uses rtl_433 to catch info from 433Mhz sensors and put it into file.
This file can be used in weewx using fileparse plugin

copy weewx_rtl_433.py to /usr/bin and execute.
the script starts /usr/bin/rtl_433 and uses pipes to catch incomming data

To check if signals are recognized, just fireup rtl_433 and watch incomming traffic.
Adapt the script to match your sensors and output. It now only works for sensors with matching ID's
so probably will need attention!

Work in progress...

ps. I made a change to rtl_433 to only produce stdout messages. It is send to source to be included so should be in release soon. I only read stdout qeueu from rtl_433.
