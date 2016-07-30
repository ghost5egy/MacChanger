import sys
import os

if sys.platform == 'win32':
    import ctypes

import pygtk
pygtk.require('2.0')
import gtk
import locale
from spoofmac.version import __version__
from spoofmac.util import random_mac_address, MAC_ADDRESS_R, normalize_mac_address

from spoofmac.interface import (
	wireless_port_names,
	find_interfaces,
	find_interface,
	set_interface_mac,
	get_os_spoofer
)


# Return Codes
SUCCESS = 0
INVALID_ARGS = 1001
UNSUPPORTED_PLATFORM = 1002
INVALID_TARGET = 1003
INVALID_MAC_ADDR = 1004
NON_ROOT_USER = 1005

devlist = []
portlist = []

def get_intterfaces():

	spoofer = get_os_spoofer()
	targets = []
	line = []

	for port, device, address, current_address in spoofer.find_interfaces(targets=targets):
		devlist.append(device)
		portlist.append(port)
		print port, device, address, current_address

class mywindow(gtk.Window):

	def __init__(self):
		gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
		self.Mainbox = gtk.HBox(spacing = 6);
		self.add(self.Mainbox)
		self.thirdbox = gtk.VBox(spacing = 6);
		self.Mainbox.pack_start(self.thirdbox,True,True,5)
		self.label = gtk.Label("Network Card")
		self.thirdbox.pack_start(self.label,True,True,5)
		self.label1 = gtk.Label("New MAc")
		self.thirdbox.pack_start(self.label1,True,True,5)
		self.label2 = gtk.Label("")
		self.thirdbox.pack_start(self.label2,True,True,5)
		self.firstbox = gtk.VBox(spacing = 6);
		self.Mainbox.pack_start(self.firstbox,True,True,5)
		self.entry = gtk.Combo()
		self.entry.set_popdown_strings(devlist)
		self.entry.entry.set_text("Choose Network Card")
		self.firstbox.pack_start(self.entry,True,True,5)
		self.entry1 = gtk.Entry()
		self.firstbox.pack_start(self.entry1,True,True,5)
		self.button = gtk.Button(label="Set Mac")
		self.button.connect("clicked",self.on_bt_click)
		self.firstbox.pack_start(self.button,True,True,5)
		self.label3 = gtk.Label("Choose Network Card")
		self.firstbox.pack_start(self.label3,True,True,5)
		
	def on_bt_click(self, widget):
		try:
			root_or_admin = os.geteuid() == 0
		except AttributeError:
			root_or_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
		
		if self.entry.entry.get_text() == ("Choose Network Card"):
			print "Choose from combo\n"
		elif self.entry1.get_text() == (""):
			print "Enter New Mac Address\n"
			self.label3.set_text("Enter New Mac Address")
		else:
			spoofer = None

			try:
				spoofer = get_os_spoofer()
			except NotImplementedError:
				return UNSUPPORTED_PLATFORM
			result = find_interface(self.entry.entry.get_text())
			if result is None:
				print('- couldn\'t find the device for {target}'.format(
					target=target
				))
				self.label3.set_text("Couldn't find device ")
				return INVALID_TARGET
				
			port, device, address, current_address = result			
			target_mac = self.entry1.get_text()
			if int(target_mac[1], 16) % 2:
				self.label3.set_text("It's Multicast Address")
				print('Warning: The address you supplied is a multicast address and thus can not be used as a host address.')
			
			if not MAC_ADDRESS_R.match(target_mac):
				print('- {mac} is not a valid MAC address'.format(
					mac=target_mac
				))
				return INVALID_MAC_ADDR

			if not root_or_admin:
				if sys.platform == 'win32':
					print('Error: Must run this with administrative privileges to set MAC addresses')
					self.label3.set_text("You Need to run as admin")
					return NON_ROOT_USER
				else:
					print('Error: Must run this as root (or with sudo) to set MAC addresses')
					self.label3.set_text("You Need to run as root")
					return NON_ROOT_USER
			asd = set_interface_mac(device, target_mac, port)
			print asd
			print "Mac Changed\n"
			self.label3.set_text("Mac Changed")
			
		print self.entry.entry.get_text()
		print self.entry1.get_text()
		
get_intterfaces()
print devlist
print portlist
win = mywindow()
win.set_title("Mac Changer")
win.connect("delete-event",gtk.main_quit)
win.show_all()
gtk.main()
