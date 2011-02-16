#!/usr/bin/env python

# Author: 	Sankar P <sankar.curiosity@gmail.com>
# License:	LGPLv2.1 Only 

import gtk
import subprocess

class oscwrapper:

	#FIXME: Get the API url from the command line or a config file
	command = "osc -A http://api.opensuse.org"

	def getProjects(self):
		# As of now, I am using osc directly. Ideally, we should have a library.
		p = subprocess.Popen([oscwrapper.command + " my prj -m"], shell=True, stdout=subprocess.PIPE)
		out, err = p.communicate()
		return out.split()

class gosc:
	def __init__(self, wrapper):
		window = gtk.Window()
		window.maximize()

		liststore = gtk.ListStore(str)
		treeview = gtk.TreeView(liststore)
	
		#FIXME: Blocking on the main thread.
		projects = wrapper.getProjects()
		for item in projects:
			liststore.append([item])
	
		projects_column = gtk.TreeViewColumn("Projects")
		treeview.append_column(projects_column)
	
		cell = gtk.CellRendererText()
		projects_column.pack_start(cell, False)
		projects_column.add_attribute(cell, "text", 0)
	
		window.connect("destroy", lambda w: gtk.main_quit())
	
		window.add(treeview)
		window.show_all()

wrapper = oscwrapper()
gosc(wrapper)
gtk.main()
