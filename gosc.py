#!/usr/bin/env python

# Author: 	Sankar P <sankar.curiosity@gmail.com>
# License:	LGPLv2.1 Only 

import gtk
import subprocess

class oscwrapper:

	#FIXME: As of now, I am using osc directly. Ideally, we should have a library.

	#FIXME: Get the API url from the command line or a config file
	command = "osc -A https://api.opensuse.org"

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

	def getRepositories(self, project):
		p = subprocess.Popen([oscwrapper.command + " repositories " + project], shell=True, stdout=subprocess.PIPE)
		out, err = p.communicate()
		return out.split('\n')

	def getPackageBuildLog(self, project, package, repository_and_arch):
		p = subprocess.Popen([oscwrapper.command + " remotebuildlog " + project + " " + package + " " + repository_and_arch], shell=True, stdout=subprocess.PIPE)
		out, err = p.communicate()
		return out

class gosc:

	packages_liststore = gtk.ListStore(str)
	build_results_area = gtk.TextView()
	selected_project = ""

	def package_double_clicked(self, treeview, path, column):
		model = treeview.get_model()
		treeiter = model.get_iter(path)
		selected_package = model.get_value(treeiter, 0)

		# get the repositories list and ask to choose a repository
		repos_liststore = gtk.ListStore(str)
		repos_treeview = gtk.TreeView(repos_liststore)
	
		repositories = wrapper.getRepositories(gosc.selected_project)
		for item in repositories:
			repos_liststore.append([item])
	
		repos_column = gtk.TreeViewColumn("Repositories")
		repos_treeview.append_column(repos_column)

		cell = gtk.CellRendererText()
		repos_column.pack_start(cell, False)
		repos_column.add_attribute(cell, "text", 0)

		repos_scroll = gtk.ScrolledWindow()
		repos_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		repos_scroll.add(repos_treeview)

		dialog = gtk.Dialog("Choose a Repository")
		dialog.vbox.add(repos_scroll)
		dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
		dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
		dialog.set_modal(True)
		dialog.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
		dialog.show_all()
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			rmodel = repos_treeview.get_model()
			rtreeiter = rmodel.get_iter(path)
			selected_repo_and_arch = rmodel.get_value(rtreeiter, 0)
		dialog.destroy()

		results = wrapper.getPackageBuildLog(gosc.selected_project, selected_package, selected_repo_and_arch)
		gosc.build_results_area.get_buffer().set_text(results)

	def project_double_clicked(self, treeview, path, column):
		model = treeview.get_model()
		treeiter = model.get_iter(path)
		gosc.selected_project = model.get_value(treeiter, 0)

		# Update packages list
		packages = wrapper.getPackages(gosc.selected_project)
		gosc.packages_liststore.clear()
		for item in packages:
			gosc.packages_liststore.append([item])

		# Get Build results for all the packages in the project
		prjresults = wrapper.getPrjResults(gosc.selected_project)
		gosc.build_results_area.get_buffer().set_text(prjresults)


	def __init__(self, wrapper):

		window = gtk.Window()
		hbox = gtk.HBox(True, 10)
		vbox = gtk.VBox(True, 10)

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
		packages_treeview.connect("row-activated", self.package_double_clicked)

		packages_scroll = gtk.ScrolledWindow()
		packages_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		packages_scroll.add(packages_treeview)
		hbox.add(packages_scroll)
		#----------------------------------
		vbox.add(hbox)

		gosc.build_results_area.get_buffer().set_text("Your projects are listed in the above list.\nDouble-clicking on any project in the above list will get the packages list and populate it on the other listview above-and-right.\nThis area will be filled with the overall build-result of the selected project.\n\nDouble clicking on a package in the other list above will get the build log for the selected package and display it in this area.")
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
