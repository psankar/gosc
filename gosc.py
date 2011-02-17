#!/usr/bin/env python

# Author: 	Sankar P <sankar.curiosity@gmail.com>
# License:	LGPLv2.1 Only 

import gtk
import subprocess

class oscwrapper:

	#FIXME: As of now, I am using osc directly. Ideally, we should have a library.

	#FIXME: Get the API url from the command line or a config file
	command = "osc -A http://api.opensuse.org"

	def getProjects(self):
		p = subprocess.Popen([oscwrapper.command + " my prj -m"], shell=True, stdout=subprocess.PIPE)
		out, err = p.communicate()
		return out.split()

	def getPackages(self, project):
		p = subprocess.Popen([oscwrapper.command + " ls " + project], shell=True, stdout=subprocess.PIPE)
		out, err = p.communicate()
		return out.split()

	def getPrjResults(self, project):
		p = subprocess.Popen([oscwrapper.command + " prjresults " + project], shell=True, stdout=subprocess.PIPE)
		out, err = p.communicate()
		return out

class gosc:

	packages_liststore = gtk.ListStore(str)
	build_results_area = gtk.TextView()

	def project_double_clicked(self, treeview, path, column):
		model = treeview.get_model()
		treeiter = model.get_iter(path)
		selected_project= model.get_value(treeiter, 0)

		# Update packages list
		packages = wrapper.getPackages(selected_project)
		gosc.packages_liststore.clear()
		for item in packages:
			gosc.packages_liststore.append([item])

		# Get Build results for all the packages in the project
		prjresults = wrapper.getPrjResults(selected_project)
		gosc.build_results_area.get_buffer().set_text(prjresults)


	def __init__(self, wrapper):

		window = gtk.Window()
		hbox = gtk.HBox(True, 0)
		vbox = gtk.VBox(True, 0)

		#----------------------------------
		# Region for setting up the Projects liststore
		#----------------------------------
		projects_liststore = gtk.ListStore(str)
		projects_treeview = gtk.TreeView(projects_liststore)
	
		#FIXME: Blocking on the main thread.
		projects = wrapper.getProjects()
		for item in projects:
			projects_liststore.append([item])
	
		projects_column = gtk.TreeViewColumn("Projects")
		projects_treeview.append_column(projects_column)
	
		cell = gtk.CellRendererText()
		projects_column.pack_start(cell, False)
		projects_column.add_attribute(cell, "text", 0)
		projects_treeview.connect("row-activated", self.project_double_clicked)

		projects_scroll = gtk.ScrolledWindow()
		projects_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		projects_scroll.add(projects_treeview)
		hbox.add(projects_scroll)
		#----------------------------------


		#----------------------------------
		# Region for setting up the Packages,
		# corresponding to the selected project.
		#----------------------------------
		packages_treeview = gtk.TreeView(gosc.packages_liststore)

		packages_column = gtk.TreeViewColumn("Packages")
		packages_treeview.append_column(packages_column)
	
		pkg_cell = gtk.CellRendererText()
		packages_column.pack_start(pkg_cell, False)
		packages_column.add_attribute(pkg_cell, "text", 0)

		packages_scroll = gtk.ScrolledWindow()
		packages_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		packages_scroll.add(packages_treeview)
		hbox.add(packages_scroll)
		#----------------------------------
		vbox.add(hbox)

		gosc.build_results_area.get_buffer().set_text("Build results should come here")
		gosc.build_results_area.set_editable(False)

		build_results_scroll = gtk.ScrolledWindow()
		build_results_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		build_results_scroll.add(gosc.build_results_area)
		vbox.add(build_results_scroll)

		window.add(vbox)
		window.maximize()
		window.connect("destroy", lambda w: gtk.main_quit())
		window.show_all()

wrapper = oscwrapper()
gosc(wrapper)
gtk.main()
