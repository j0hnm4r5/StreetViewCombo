from PIL import Image
import urllib2, json
import os, random
from datetime import datetime

address = "938 charlton rd, scotia, ny 12302"

def download_image(latitude, longitude, width=400, height=400, fov=110, heading=0, pitch=20):

	img_url = "https://maps.googleapis.com/maps/api/streetview?size=" + str(width) + "x" + str(height) + "&location=" + str(latitude) + "," + str(longitude) + "&fov=" + str(fov) + "&heading=" + str(heading) + "&pitch=" + str(pitch)
	request = urllib2.Request(img_url)
	img = urllib2.urlopen(request).read()
	with open('img/' + str(latitude) + "_" + str(longitude) + '.jpg', 'w') as f:
		f.write(img)
	return 'img/' + str(latitude) + "_" + str(longitude) + '.jpg'

def geolocate(address):
	location_url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address.replace(" ", "+")
	data = json.loads(urllib2.urlopen(location_url).read())
	return data['results'][0]['geometry']['location']

located = geolocate(address)

im1_loc = download_image(located['lat'], located['lng'])
im2_loc = "img/" + str(random.choice(os.listdir("img/")))

while (im1_loc == im2_loc):
	im2_loc = "img/" + str(random.choice(os.listdir("img/")))

im1 = Image.open(im1_loc)
im2 = Image.open(im2_loc)

mask = Image.open('mask.png').convert("L")

composite1 = Image.composite(im2, im1, mask)
composite2 = Image.composite(im1, im2, mask)

margin = 20
new_im = Image.new('RGB', (im1.size[0] + im2.size[0] + margin * 3, im1.size[1] + margin * 2), "white")

new_im.paste(composite2, (margin, margin))
new_im.paste(composite1, (margin * 2 + composite1.size[0], margin))
new_im.save("composites/" + datetime.now().strftime('%Y%m%dT%H%M%S') + '.jpg')
