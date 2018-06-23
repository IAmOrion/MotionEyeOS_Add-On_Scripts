# MotionEyeOS_Add-On_Scripts
MotionEyeOS Add-On Scripts for Push Notifications (via Pushover) as well as ANPR/ALPR (via OpenALPR)

# /Basic

The "Basic" folder contains scripts that are, well, basic.  They are pretty much self contained, and by editing the file with a text editor, most people (including relative novices) should be able to get them working for their needs.  The catch of course, if you were using multiple cameras on a single Pi device, you would need multiple copies of each script, modified to for each camera so to speak.  That's where there the Advanced folder comes in...

# /Advanced

These scripts are less novice friendly, but are built to parse command line arguments, meaning all options parsed with the command line.  For example: python script.py --arg1 --arg2 --arg3 and so on.  This has the benefit of MUCH neater code, as well as being able to use the same script for multiple cameras, simply by parsing different arguments.

# /Images

Images used in some of the scripts
