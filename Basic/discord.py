# ================================================================================
# Discord webhook script for MotionEyeOS - James Tanner aka IAmOrion
# ================================================================================

global MESSAGE, FILENAME, FILE_FOUND

# ================================================================================
# Script Settings
# ================================================================================

WEBHOOK_URL="YOUR_WEBHOOK_URL"
WEBHOOK_HEADER = "Content-Type: multipart/form-data" # Leave this as is! DO NOT CHANGE THIS!!!!
WEBHOOK_TITLE = "__**Motion Detected!**__\n\n" # Check Discords mark down text to see how to style your content.  \n = new lne
WEBHOOK_MESSAGE = " - Motion was detected on Camera 1"

OVERRIDE_TIMEZONE = 0 # 1 Override timezone or 0 use MotionEye set timezone
OVERRIDE_TIMEZONE_WITH = "Europe/London" # Only used is above is set to 1

NETWORK_SHARE = 1 # Are you using a network share for storage? 1 = yes, 0 = no
SHARE_FOLDER = '/data/media/motioneye_192_168_0_200_storage_sda1_front_cctv_rpizerow_cam2__admin/' # Only required if NETWORK_SHARE = 1
				# You will need to use SFTP or SSH to find the path above.  
				# Goto /data/media/ and you will see the name of your mapped network folder

if NETWORK_SHARE:
	# You will have to build/code this string manually depending on your usage and how you're saving still images.  
	# Look below to see how this is currently done.  The function is find_latest_file():  
	# This was written to match my setup, eg folder are stored in d-m-y format.  Eg: ./22-06-2018/21-00-00.jpg
	FIND_LATEST_FILE = 1
else:
	#FILENAME = '/data/output/noimage.jpg'
	FILENAME = '/data/output/Camera1/lastsnap.jpg'
	
PYCURL_VERBOSE = False # Can be useful for debugging the http post.  True / False

DEBUG = 0 # If set to 1, the response from Discord will be output in terminal.  Useful when testing manually

# ================================================================================
# Do not edit below this line unless you know what you're doing!
# ================================================================================

import pycurl, cStringIO, glob, os, json, pytz, datetime, time

if OVERRIDE_TIMEZONE:
	TIMEZONE = OVERRIDE_TIMEZONE_WITH
else:
	TIMEZONE = os.path.realpath('/data/etc/localtime').replace('/usr/share/zoneinfo/posix/','')

utc = pytz.timezone('UTC')
now = utc.localize(datetime.datetime.utcnow())
la = pytz.timezone(TIMEZONE)
local_time = now.astimezone(la)

CURRENT_TIME = local_time.strftime('%Y-%m-%dT%H:%M:%S.000Z') # UTC Formatted for use in Discords timestamp argument
MESSAGE_TIME = local_time.strftime(MESSAGE_DATEFORMAT)

#WEBHOOK_CONTENT = { "content": "__**MotionEyeOS - Motion Detected!**__\n\nMotion was detected on camera 1","embeds": [{"author":{ "name": "MotionEyeOS", "icon_url": "https://raw.githubusercontent.com/IAmOrion/MotionEyeOS_Add-On_Scripts/master/icon.png"},"timestamp": CURRENT_TIME }] }
WEBHOOK_CONTENT = { "content": WEBHOOK_TITLE + MESSAGE_TIME + WEBHOOK_MESSAGE,"embeds": [{"timestamp": CURRENT_TIME }] }

def find_latest_file():
	global FILE_FOUND, FILENAME
	FILE_FOUND = 0
	TODAYS_DATE = datetime.datetime.today().strftime('%d-%m-%Y')
	TODAYS_DATE_FOLDER = SHARE_FOLDER + TODAYS_DATE + '/*.jpg'

	LIST_OF_FILES = glob.glob(TODAYS_DATE_FOLDER) # * means all, if need specific format then *.jpg (as an example).  Just FYI - MotionEye stores still images as jpg
	
	try:

		LATEST_FILE = max(LIST_OF_FILES, key=os.path.getctime)
		FILE_FOUND = 1

	except ValueError:

		FILE_FOUND = 0
	
	if FILE_FOUND:

		FILENAME = LATEST_FILE

	else: 
		FILENAME = '/data/output/noimage.jpg'
		
def send_to_discord():
	
	buf = cStringIO.StringIO()

	c = pycurl.Curl()
	c.setopt(c.URL, WEBHOOK_URL)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.setopt(c.HTTPHEADER, [WEBHOOK_HEADER])
	c.setopt(c.USERAGENT, "MotionEyeOS")

	if os.path.isfile(FILENAME):
		c.setopt(c.HTTPPOST, [("payload_json", json.dumps(WEBHOOK_CONTENT)),("file", (c.FORM_FILE, FILENAME, )),])
	else:
		c.setopt(c.HTTPPOST, [("payload_json", json.dumps(WEBHOOK_CONTENT)),])
	
	c.setopt(c.VERBOSE, PYCURL_VERBOSE)
	
	c.perform()
	c.close()
	
	f = buf.getvalue()
	buf.close()
	
	if DEBUG:
	
		print(f)
		
		
print("\n================================================================================")
print(" MotionEyeOS - Motion Detected, Running Discord Script... ")
print("================================================================================\n")

if NETWORK_SHARE:

	find_latest_file()
	
	print("Finding last captured still image...")
	
send_to_discord()

print("\n================================================================================")
print(" MotionEyeOS - Motion Detected, Discord Script Completed ")
print("================================================================================\n")
