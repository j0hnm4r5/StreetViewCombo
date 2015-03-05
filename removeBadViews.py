from PIL import Image
import os, random

for loc in os.listdir("img"):
	im = Image.open("img/" + loc)
	if im.getpixel((50, 50)) == (228, 227, 223):
		os.remove("img/" + loc)
