from bottle import *

from PIL import Image
import urllib2, json
import os, random
from datetime import datetime

address = ""

# allow server to display images in /composites
@route('/composites/<filename>')
def send_image(filename):
	return static_file(filename, root='./composites')

# allow server to access css files
@route('/css/<filename>')
def send_image(filename):
    return static_file(filename, root='./css')

# route root and display address.tpl
@get('/')
def ask():
	return template('address')

# route form submission and display image.tpl
@post('/')
def do_ask():
	address = request.forms.get('address')

	located = geolocate(address)

	# pick two images to composite
	im1_loc = download_image(located['lat'], located['lng'])
	im2_loc = "img/" + str(random.choice(os.listdir("img/")))

	# if the images are the same, try again
	while (im1_loc == im2_loc):
		im2_loc = "img/" + str(random.choice(os.listdir("img/")))

	im1 = Image.open(im1_loc)
	im2 = Image.open(im2_loc)

	# import mask image
	mask = Image.open('mask.png').convert("L")

	# make composite images
	composite1 = Image.composite(im2, im1, mask)
	composite2 = Image.composite(im1, im2, mask)

	# make new image to place composites within
	margin = 20
	new_im = Image.new('RGB', (im1.size[0] + im2.size[0] + margin * 3, im1.size[1] + margin * 2), "white")

	# place composites
	new_im.paste(composite2, (margin, margin))
	new_im.paste(composite1, (margin * 2 + composite1.size[0], margin))
	new_im_loc = datetime.now().strftime('%Y%m%dT%H%M%S') + ".jpg"
	new_im.save("composites/" + new_im_loc)

	# Don't keep "No imagery at this location" images
	if im1.getpixel((50, 50)) == (228, 227, 223):
		os.remove(im1_loc)

	return template('image', img_url=new_im_loc)

def download_image(latitude, longitude, width=400, height=400, fov=110, heading=0, pitch=20):

	"""
	Downloads and returns image from Google Street View API from specific latitude and longitude
	"""

	img_url = "https://maps.googleapis.com/maps/api/streetview?size=" + str(width) + "x" + str(height) + "&location=" + str(latitude) + "," + str(longitude) + "&fov=" + str(fov) + "&heading=" + str(heading) + "&pitch=" + str(pitch)
	request = urllib2.Request(img_url)
	img = urllib2.urlopen(request).read()
	with open('img/' + str(latitude) + "_" + str(longitude) + '.jpg', 'w') as f:
		f.write(img)
	return 'img/' + str(latitude) + "_" + str(longitude) + '.jpg'

def geolocate(address):
	"""
	Returns latitude and longitude for supplied address
	"""
	location_url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address.replace(" ", "+")
	data = json.loads(urllib2.urlopen(location_url).read())
	return data['results'][0]['geometry']['location']


# run the server
run(host='localhost', port=8989, debug=True)
