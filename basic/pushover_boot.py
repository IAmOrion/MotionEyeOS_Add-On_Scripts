import httplib, urllib

# Pushover Settings - https://pushover.net
# ================================================================================

APP_TOKEN = 'YOUR_APP_TOKEN'
USER_KEY = 'YOUR_USER_KEY'
HTML = '1'
TITLE = 'MotionEyeOS (Re)booted'
MESSAGE = '<b>RPiZeroW_CAM2</b><br><br>This camera device has just (re)booted and is now up and running'
URL = '' # Enter a URL if you would like there to be a link to something in the notification.  Useful if you have port forwarding for example, and want to provide a link to the camera 
URL_TITLE = '' # Text shown for the url link
SOUND = 'cosmic' # default = pushover. https://pushover.net/api#sounds

conn = httplib.HTTPSConnection("api.pushover.net:443")
conn.request("POST", "/1/messages.json",
urllib.urlencode({
  "token": APP_TOKEN,      # Pushover app token
  "user": USER_KEY,        # Pushover user token
  "html": HTML,           # 1 for HTML, 0 to disable
  "title": TITLE,      # Title of message
  "message": MESSAGE,  # Message (HTML if required)
  "url": URL,           # Link to include in message
  "url_title": URL_TITLE,     # Text for link
  "sound": "cosmic",     # Sound played on receiving device
}), { "Content-type": "application/x-www-form-urlencoded" })
response = conn.getresponse()
print response.status, response.reason
data = response.read()
conn.close()
