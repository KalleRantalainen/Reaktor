"""
File: scraping.py
Programmer: Kalle Rantalainen
Email: kalle.rantalainen@tuni.fi
Date: 13.01.2023

This file is used to scrape and process information found
from:
	- https://assignments.reaktor.com/birdnest/drones
	- https://assignments.reaktor.com/birdnest/pilots/...
This file writes the information about drone pilots that
have broken the no-fly zone for 10 minutes. The information
is stored to pilot_information.json and information.html files.
This file is called from the keep_alive.py file every 2 seconds.
So the pilot_information.json and the information.html is
updated every 2 seconds.
"""


# Importing libraries that are needed in this file
from bs4 import BeautifulSoup
import requests
import json
from math import sqrt
import datetime


def check_forbidden_coords(data):
	"""
	No fly zone (NFZ) is circle with radius of 100 000 at position
	(250 000, 250 000). The drone pilot is not allowed to enter
	this circle. This function reads the xml file from the web
	and checks if any of the pilots in the 500 000 x 500 000 area
	is in the circle.
	:return: Dictionary which keys are serial_numbers of drones
	and value is time that when the pilot violated the no drone zone
	and the distance between the drone and the nest.
	"""
	# We can extract drone information from the data and
	# make a list that includes every drone and information
	# about them.
	drones = data.find_all("drone")

	# Next we need to find every drone which coordinates
	# are illegal. We store the illegal drone's serial number
	# to dict called illegal_drone_ids

	illegal_drone_ids = {}

	for drone in drones:
		x_coord_str = str(drone.find("positionX"))
		y_coord_str = str(drone.find("positionY"))

		# Now each coordinate is in format "<position>xxxxx.xxxxx</position>"
		# and we only want the number inside position tags
		x_coord_splitted = str(x_coord_str).split(">")[1].split("<")[0]
		y_coord_splitted = str(y_coord_str).split(">")[1].split("<")[0]

		# Converting the number into float so we can use them to
		# calculate distance.
		x_coord = float(x_coord_splitted)
		y_coord = float(y_coord_splitted)

		# Now we can check if coords are illegal. We can also calculate
		# the distance from drone's coordinates to (250000, 250000)
		# with equation d = sqrt((x1-x2)^2+(y1-y2)^2). We can detect
		# the time drone violated the nfz
		if 150000 < x_coord < 350000:
			# x_coord is inside of the nfz. (this could also
			# be done with y_coord nut I chose x.) Now we can
			# calculate the distance to the drone position
			# form the nest location. If the distance is
			# 100 or less than 100, then the y_coordinate is
			# also inside of the nfz and we can add the
			# drones serial number to illegal drones dict.
			distance = sqrt((250000 - x_coord) ** 2 + (250000 - y_coord) ** 2)

			if distance <= 100000:
				# Drone is inside the nfz
				ser_num_str = str(drone.find("serialNumber"))
				ser_num = str(ser_num_str).split(">")[1].split("<")[0]
				time = datetime.datetime.now()
				illegal_drone_ids[ser_num] = [str(time), distance]

	return illegal_drone_ids



def get_pilot_data(drones_in_nfz):
	"""
	This function scrapes data off of every pilot who has
	violated the nfz. All of these pilots can be found
	with the drones_in_nfz because it contains all the
	serial numbers for the drones in the nfz. This function
	also updates the information scraped from the web into
	pilot_information.json file.
	"""
	# url for the pilot information is in format
	# https://assignments.reaktor.com/birdnest/pilots/_____
	# where the last part is drone's serial number. We can
	# get information from every person that has violated
	# the nfz with replacing the last part with the drone's
	# serial number.
	url = "https://assignments.reaktor.com/birdnest/pilots/"

	# We have a dict of drone serial numbers that violated
	# the nfz recently. The dict also contains the time of
	# violation and the closest distance to the nest. We
	# calculated these in the check_forbidden_coords()
	# function.
	# Pilot information is stored into dict called pilot_data.
	pilot_data = {}

	for drone in drones_in_nfz:
		# Adding the drone's serial number to the url.
		new_url = url + drone

		# Getting the json formatted data from the website.
		json_data = requests.get(new_url).content

		# json data is turned into pyhton dict so we can easily
		# modify it with python.
		json_object = json.loads(json_data)

		# Because the data does not include information when
		# the drone violated the nfz, we need to add it. We
		# also want to add the closest distance from the nest
		# to the dict.
		json_object["timeOfViolation"] = drones_in_nfz[drone][0]
		json_object["closestDistance"] = drones_in_nfz[drone][1]

		# Storing the modified json data into pilot_data dict
		# pilotId as a key.
		pilot_data[json_object["pilotId"]] = json_object

	# saved_pilot_info is a dict to which we can load information
	# that we have gotten previously from the pilots.
	saved_pilot_info = {}

	with open("pilot_information.json") as json_file:
		# Sometimes there is a error in opening the jason
		# file and this try - except catches it.
		try:
			# Loading info about previously encountered criminal pilots
			# into saved_pilot_info dict from file pilot_information.json
			saved_pilot_info = json.load(json_file)

			# Looping through the newly acquired pilot data
			# to see if the old data already contains the pilot
			# or if the pilot is new. Then we update the
			# saved_pilot_info accordingly.
			for pilot_id in pilot_data:
				if pilot_id in saved_pilot_info.keys():
					# The pilot has already broken the law in the past
					# 10 minutes, so we need to update the time of violation.
					saved_pilot_info[pilot_id]["timeOfViolation"] = pilot_data[pilot_id]["timeOfViolation"]

					if saved_pilot_info[pilot_id]["closestDistance"] > pilot_data[pilot_id]["closestDistance"]:
						# The pilot got closer to the nest this time than
						# previously so we need to update the closest
						# drones closest distance to the nest.
						saved_pilot_info[pilot_id]["closestDistance"] = pilot_data[pilot_id]["closestDistance"]
				else:
					# The pilot wasn't in the dict before so
					# we can make new element to the dict containing
					# pilot_id as key and data of the pilot as value.
					saved_pilot_info[pilot_id] = pilot_data[pilot_id]
			json_file.close()
		except json.decoder.JSONDecodeError:
			# catching error
			print("Errori tulee ilmeisesti tyhjästä json tiedososta")

	# to_be_deleted is a list in which we can push all the pilots
	# we might want to delete from the saved_pilot_info. We want to delete
	# the information in case that the pilot violated
	# the no fly zone 10 minutes ago.
	to_be_deleted = []

	for pilot_id in saved_pilot_info:
		# Getting current time
		time_now = datetime.datetime.now()
		# Getting the last time when the pilot violated the
		# nfz from the saved_pilot_data. And formatting the
		# string data back to datetime object.
		time_of_violation = datetime.datetime.\
			strptime(saved_pilot_info[pilot_id]["timeOfViolation"],
					 '%Y-%m-%d %H:%M:%S.%f')

		# Because both times are now datetime object
		# we can just simply subtract the previous
		# time of violation from current time and
		# see if the crime happened over 10 minutes ago.
		difference = time_now - time_of_violation

		# Appending the pilot_id to the to_be_deleted list
		# if the crime happened over 600 seconds -> 10 minutes ago.
		if difference.seconds > 600:
			to_be_deleted.append(pilot_id)

	# Deleting all of the pilots from the dict if
	# they were last seen in the nfz over 10 minutes
	# ago.
	for key in to_be_deleted:
		del saved_pilot_info[key]

	# Now we can update the pilot_information file
	with open("pilot_information.json", "w") as writing_file:
		json.dump(saved_pilot_info, writing_file, indent=4)
	writing_file.close()


def get_drone_data():
	"""
	Getting the data that includes for example the drone coordinates
	and the drones serial number from the web.
	:return: returns the data of all of the drones in the 500x500m square.
	"""
	# url to the drone data website
	url = "https://assignments.reaktor.com/birdnest/drones"

	# The data is in xml format and is saved
	# to variable called xml data.
	xml_data = requests.get(url).content

	# BeautifulSoup makes the xml data into prettier
	# form and we can use to get information.
	soup = BeautifulSoup(xml_data, "xml")
	soup.prettify()

	return soup


def convert_info_into_html():
	"""
	This function converts all off the data that we have
	gotten from the web pages and prosessed with function in
	this file into a html format. The data is then saved
	into html file.
	"""

	with open("pilot_information.json") as json_file:
		json_object = json.load(json_file)
	json_file.close()

	# The html file always consists these lines
	# off code so no matter how many pilots have
	# visited the no fly zone, the html file
	# will always have these lines in it. Now if
	# we have gathered information about criminal drone
	# pilots, we can append the information into this list
	# between the </h1> an </body> tag so in the -2 index
	# of the list. The base also includes tag
	# <meta http-equiv="refresh" content="2"> which causes
	# the web page tp auto refresh in every 2 seconds.
	base_html = ['<!DOCTYPE html>\n', '<html lang="en">\n',
				 '    <head>\n', '    <meta charset="UTF-8"><title>NFZ</title>\n',
				 '    <meta http-equiv="refresh" content="2">\n',
				 '    <title> NFZ </title>\n',
				 '    </head>\n', '<body>\n',
				 '    <h1 style="font-family: Arial">\n',
				 '        Pilots that recently violated the NFZ\n',
				 '    </h1>\n', '</body>\n', '</html>']

	# going through the dict that contains
	# information about the law breakers
	for pilot_id in json_object:
		# Saving the pilot name in a html format in
		# variable called html_name. The same is done
		# to all information that needs to be shown on
		# the web page.
		html_name = f'<h3 style="font-family: Arial"> Pilot:' \
					f' {json_object[pilot_id]["firstName"]}' \
					f' {json_object[pilot_id]["lastName"]} </h3>\n'
		html_phone = f'<p style="font-family: Arial"> Phone number:' \
					 f' {json_object[pilot_id]["phoneNumber"]} </p>\n'
		html_email = f'<p style="font-family: Arial"> Email address:' \
					 f' {json_object[pilot_id]["email"]} </p>\n'
		html_dis = f'<p style="font-family: Arial"> Closest distance to the nest:' \
				   f' {float(json_object[pilot_id]["closestDistance"])/1000:.2f}' \
				   f' meters. </p>\n'
		# Inserting the information into base_html list
		base_html.insert(-2, html_name)
		base_html.insert(-2, html_phone)
		base_html.insert(-2, html_email)
		base_html.insert(-2, html_dis)

	# If the third last element is '    </h1>\n,
	# then there has not been any violations in the nfz
	# for the past 10 minutes.
	if str(base_html[-3]) == '    </h1>\n':
		# No one has been in the nfz fro 10 minutes
		base_html.insert(-2, '<p style="font-family: Arial"> No drones seen in the'
							 ' NFZ for 10 minutes </p>')

	# Opening the html file of the web page.
	html_file_object = open("templates/information.html", "w")

	# Writing the file again with new updated information
	for line in base_html:
		html_file_object.write(line)

	html_file_object.close()



def update_web_page():
	"""
	This is kind of a main function for this file.
	This function is called every 2 seconds or when
	a user updates the website. This function is
	called from the keep_alive.py files home function
	to update the information on the webpage.
	"""
	# Getting the data of all the drones that
	# the device has detected in the 500x500m square.
	drone_data = get_drone_data()

	# Calculating if some of the drones are in the no
	# drone/ no fly zone.
	drones_in_nfz = check_forbidden_coords(drone_data)

	# Getting data of the pilots that went to the
	# no drone zone with their drones.
	get_pilot_data(drones_in_nfz)

	# Lastly converting all of the data into html fromat and
	# updating the html file which results the web page
	# being updated.
	convert_info_into_html()

