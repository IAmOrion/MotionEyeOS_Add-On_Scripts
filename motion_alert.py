# ================================================================================
# Script Settings
# ================================================================================

global MESSAGE, FILENAME, FILE_FOUND

# In all settings that act as a boolean (true or false) option, 0 = false, 1 = true

# Shared Settings (Including MotionEyeOS Settings)
# ================================================================================

PUSHOVER = 1 # 1 = Use | 0 = Don't use
OPENALPR = 1 # 1 = Use | 0 = Don't use

DELAY = 5 # Delay in seconds before processing the captured image.  Reason for this, is due to processor speed, (PiZeroW at least) the script is actioned before the motion triggered image is saved!)

NETWORK_SHARE = 1 # Are you using a network share for storage? 1 = yes, 0 = no
SHARE_FOLDER = '/data/media/motioneye_192_168_0_200_storage_sda1_front_cctv_rpizerow_cam2__admin/' # Only required if NETWORK_SHARE = 1

# The share folder above can be retried by going into your /data/media/ folder AFTER setting up your network storage folder within MotionEye

if NETWORK_SHARE:
	# You will have to build/code this string manually depending on your usage and how you're saving still images
	FIND_LATEST_FILE = 1
else:
	FILENAME = '/data/output/Camera1/lastsnap.jpg' # lastsnap.jpg is an alias created & updated by MotionEye to always point to the "latest" / last captured still image

debug = 1 # debugging.  Obviously debugging & print statements are only useful if you're running this script manually before settings it as your motion detected notification command.

# Pushover Settings - https://pushover.net
# ================================================================================

APP_TOKEN = 'YOUR_APP_TOKEN'
USER_KEY = 'YOUR_USER_KEY'
HTML = '1' # This is a STRING - NOT a boolean! 0 = plain text, 1 = HTML
TITLE = 'MotionEyeOS - Motion Detected'
MESSAGE = '<b>RPiZeroW_CAM2</b><br><br>'
URL = ''
URL_TITLE = ''
SOUND = 'pushover' # default = pushover. https://pushover.net/api#sounds

# OpenALPR Cloud API Settings - https://cloud.openalpr.com/cloudapi/
# ================================================================================

SECRET_KEY = 'YOUR_SECRET_KEY' # Find your secret key in your CloudALPR API account
COUNTRY_CODE = 'COUNTRY_CODE' # See OpenALPR API page
RECOGNIZE_VEHICLE = '1' # 0 = Returns plate only, 1 = Returns plate and vehicle details such as make, model, colour, year.  Note: This is NOT a boolean - this is a STRING

VEHICLE_DETAILS_IN_PUSHOVER = 1 # 1 = Use | 0 = Don't use

save_results = 1 # 0 = false, 1 = true -> save the returned results to a file?
save_filename = 'results.json'

print_response = 0 # 1/0 - print() results

# ================================================================================

import pycurl
import cStringIO
import json
import glob
import os
import datetime
import time

from pprint import pprint

def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    if isinstance(data, unicode):
        return data.encode('utf-8')
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    return data
    
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


def send_pushover():

	global FILENAME
	buf = cStringIO.StringIO()

	c = pycurl.Curl()
	c.setopt(c.URL, 'https://api.pushover.net/1/messages.json')
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.setopt(c.HTTPPOST, [("token", APP_TOKEN),("user", USER_KEY),("html", HTML),("title", TITLE),("message", MESSAGE),("url", URL),("url_title", URL_TITLE),("sound", SOUND),("attachment", (c.FORM_FILE, FILENAME, )),])

	c.perform()
	c.close()

	f = buf.getvalue()
	buf.close()

	#responce = json.loads(f)
	responce = json_loads_byteified(f)

	if debug:
		
		pprint(responce)

def send_alpr():

	buf = cStringIO.StringIO()
	global MESSAGE, FILENAME

	c = pycurl.Curl()
	c.setopt(c.URL, 'https://api.openalpr.com/v2/recognize?secret_key=' + SECRET_KEY + '&recognize_vehicle=' + RECOGNIZE_VEHICLE + '&country=' + COUNTRY_CODE + '&return_image=0&topn=10')
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.setopt(c.HTTPPOST, [('image', (c.FORM_FILE, FILENAME, )),])
	c.perform()
	c.close()

	f = buf.getvalue()
	buf.close()

	#responce = json.loads(f)
	responce = json_loads_byteified(f)

	if save_results:
		file = open(save_filename, 'w')
		file.write(f)
		file.close()

	if print_response:

		pprint(responce)

	if len(responce['results']) > 0:

		if RECOGNIZE_VEHICLE:
			
			if debug:
				
				print("\nLicense Plate: " + responce['results'][0]['plate'])
				print("Vehicle: " + responce['results'][0]['vehicle']['make_model'][0]['name'].title().replace("_"," "))
				print("Year: " + responce['results'][0]['vehicle']['year'][0]['name'].title())
				print("Color: " + responce['results'][0]['vehicle']['color'][0]['name'].title())
				print("\nOpenALPR Credits Used: " + str(responce['credits_monthly_used']) + " out of " + str(responce['credits_monthly_total']) + "\n")

			if VEHICLE_DETAILS_IN_PUSHOVER:

				MESSAGE += "License Plate: " + responce['results'][0]['plate'] + "<br>"
				MESSAGE += "Vehicle: " + responce['results'][0]['vehicle']['make_model'][0]['name'].title().replace("_"," ") + "<br>"
				MESSAGE += "Year: " + responce['results'][0]['vehicle']['year'][0]['name'].title() + "<br>"
				MESSAGE += "Color: " + responce['results'][0]['vehicle']['color'][0]['name'].title() + "<br><br>"
				MESSAGE += "OpenALPR Credits Used: " + str(responce['credits_monthly_used']) + " out of " + str(responce['credits_monthly_total']) + "<br>"
			
		else:
		
			if debug: 

				print("\nLicense Plate: " + responce['results'][0]['plate'])
				print("\nOpenALPR Credits Used: " + str(responce['credits_monthly_used']) + " out of " + str(responce['credits_monthly_total']) + "\n")

			if VEHICLE_DETAILS_IN_PUSHOVER:

				MESSAGE += "License Plate: " + responce['results'][0]['plate'] + "<br><br>"
				MESSAGE += "OpenALPR Credits Used: " + str(responce['credits_monthly_used']) + " out of " + str(responce['credits_monthly_total']) + "<br>"

	else:

		if debug:

			print("\nNo vehicle data found")
			print("\nCredits Used: " + str(responce['credits_monthly_used']) + " out of " + str(responce['credits_monthly_total']) + "\n")

		if VEHICLE_DETAILS_IN_PUSHOVER:

			MESSAGE += "Motion detected! No vehicle data found (There may not have been a vehicle in the picture for ALPR to work with)<br><br>"
			MESSAGE += "OpenALPR Credits Used: " + str(responce['credits_monthly_used']) + " out of " + str(responce['credits_monthly_total']) + "<br>"

print("\n================================================================================")
print(" MotionEyeOS - Motion Detected, Running Script... ")
print("================================================================================\n")


if NETWORK_SHARE:

	find_latest_file()
	
	print("Finding last captured still image")

if OPENALPR:

	send_alpr()

	print("OpenALPR sent and response received\n")

if PUSHOVER:

	send_pushover()

	print("\nPush notification sent (hopefully)")  # I haven't yet coded a repsonse handler, this just assumes the messge sent ok.

print("\n================================================================================")
print(" MotionEyeOS - Motion Detected, Script Completed ")
print("================================================================================\n")