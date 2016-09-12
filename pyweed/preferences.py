"""
Application preferences

Adapted from: https://github.com/claysmith/oldArcD/blob/master/tools/arctographer/arcmap/preferences.py

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

import os
import platform
#import logging
import ConfigParser

# TODO:  Add logging
#log = logging.getLogger("preferences")

class Preferences(object):
	"""
	Container for application preferences.
	"""
	def __init__(self):
		"""
		Initialization with default settings.
		"""
		
		# NOTE:  All preferences are saved and read in as strings bucause this is what is
		# NOTE:  used in Qt dialog initialization.
		
		self.Map = type("Map", (object,), {})()
		self.Map.projection = "robin"
		
		self.EventOptions = type("EventOptions", (object,), {})()
		self.EventOptions.minmag = "5.0"
		self.EventOptions.maxmag = "10.0"
		self.EventOptions.mindepth = "0.0"
		self.EventOptions.maxdepth = "6731.0"
		
		self.StationOptions = type("StationOptions", (object,), {})()
		self.StationOptions.network = "_GSN"
		self.StationOptions.station = "*"
		self.StationOptions.location = "*"
		self.StationOptions.channel = "?HZ"
	
	
	def save(self):
		"""
		Saves the user's preferences to ~/.pyweed/config.ini
		"""
		config = ConfigParser.SafeConfigParser()
		
		config.add_section("Map")
		for key, value in vars(self.Map).items():
			config.set("Map", key, str(value))
			
		config.add_section("EventOptions")
		for key, value in vars(self.EventOptions).items():
			config.set("EventOptions", key, str(value))
			
		config.add_section("StationOptions")
		for key, value in vars(self.StationOptions).items():
			config.set("StationOptions", key, str(value))
						
		if os.path.exists(user_config_path()) == False:
			try:
				os.makedirs(user_config_path(), 0700)
			except Exception as e:
				###log.error("Creation of user configuration directory failed with" +
				print("Creation of user configuration directory failed with" +
					  " error: \"%s\'""" % e)
				return
		f = open(os.path.join(user_config_path(), "config.ini"), "w")
		config.write(f)
	
	
	def load(self):
		"""
		Loads the user's preferences from ~/.pyweed/config.ini
		'"""
		path = os.path.join(user_config_path(), "config.ini")
		
		if not os.path.exists(path):
			# Save the default configuration info
			try:
				self.save()
			except Exception as e:
				raise

		else:
			# Override defaults with anything found in config.ini
			f = open(path, "r")
			config = ConfigParser.SafeConfigParser()
			config.readfp(f)
	
			# NOTE:  We need to know the types of expected properties while reading them in.
			
			# Read in preferences by section
			self.set_option(config, 'Map', 'projection')
			
			self.set_option(config, 'EventOptions', 'minmag')
			self.set_option(config, 'EventOptions', 'maxmag')
			self.set_option(config, 'EventOptions', 'mindepth')
			self.set_option(config, 'EventOptions', 'maxdepth')
			
			self.set_option(config, 'StationOptions', 'network')
			self.set_option(config, 'StationOptions', 'station')
			self.set_option(config, 'StationOptions', 'locaiton')
			self.set_option(config, 'StationOptions', 'channel')
			

	def set_option(self, config, sectionName, name):
		"""Set a property on a named opreference object"""
		try:
			obj = getattr(self, sectionName)
			setattr(obj, name, config.get(sectionName, name))
		except ConfigParser.NoOptionError:
			pass

	
# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------


def user_config_path():
	"""
	Option to support different paths for different operatiing systems.

	Adapted from:  https://github.com/claysmith/oldArcD/blob/master/tools/arctographer/arcmap/datafiles.py

	@rtype: str
	@return: the directory for storing user configuration files
	"""
	if platform.system() == "Darwin":
		path = os.path.join(os.path.expanduser("~"), ".pyweed")
		return(path)
	#elif platform.system() == "Linux":
		#path = os.path.join(os.path.expanduser("~"), ".config", "pyweed")
		#return path
	#elif platform.system() == "Windows":
		#path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "pyweed")
		#return path
	else:
		raise Exception("Unsupported operating system")


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
	import doctest
	doctest.testmod(exclude_empty=True)