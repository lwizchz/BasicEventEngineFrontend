#!/usr/bin/env python

# Copyright (c) 2017 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEEF.
# BEEF is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

import wx.adv

try:
	from watchdog.observers import Observer
except ImportError:
	print("Failed to import watchdog, resources will not automatically update")

import sys
import os
import shutil
import tempfile
import tarfile
import glob
import json
import itertools
import subprocess
import queue

BEEF_VERSION_MAJOR = 0
BEEF_VERSION_MINOR = 1
BEEF_VERSION_RELEASE = 1

from ui.menubar import BEEFMenuBar
from ui.toolbar import BEEFToolBar
from ui.treectrl import BEEFTreeCtrl
from ui.notebook import BEEFNotebook
from ui.editdialog import BEEFEditDialog
if "watchdog" in sys.modules:
	from ui.filehandler import BEEFFileHandler

from core.compiler import Compiler

from resources.base import BEEFBaseResource
from resources.sprite import BEEFSprite
from resources.sound import BEEFSound
from resources.background import BEEFBackground
from resources.font import BEEFFont
from resources.path import BEEFPath
from resources.timeline import BEEFTimeline
from resources.mesh import BEEFMesh
from resources.light import BEEFLight
from resources.object import BEEFObject
from resources.room import BEEFRoom

class BEEFFrame(wx.Frame):
	def __init__(self, parent, id, file):
		wx.Frame.__init__(self, parent, id, "BEE Frontend v" + self.getVersionString(), size=(1280, 720))
		self.parent = parent
		self.ready = False

		self.callbackQueue = queue.Queue()

		self.Bind(wx.EVT_CLOSE, self.quit)

		self.gameCfg = {}

		self.resourceTypes = [
			["Sprite", "Sprites"],
			["Sound", "Sounds"],
			["Background", "Backgrounds"],
			["Font", "Fonts"],
			["Path", "Paths"],
			["Timeline", "Timelines"],
			["Mesh", "Meshes"],
			["Light", "Lights"],
			["Object", "Objects"],
			["Room", "Rooms"]
		]

		self.sprites = []
		self.sounds = []
		self.backgrounds = []
		self.fonts = []
		self.paths = []
		self.timelines = []
		self.meshes = []
		self.lights = []
		self.objects = []
		self.rooms = []

		self.images = {}
		for n, p in {
			"noimage": "images/noimage.png",
			"nosprite": "images/nosprite.png"
		}.items():
			self.images[n] = wx.Image(p)

		self.compiler = Compiler(self)

		self.init()

	def init(self):
		self.CenterOnScreen()

		self.CreateStatusBar()
		self.SetStatusText("Loading BEEF...")

		self.menubar = BEEFMenuBar(self)
		self.SetMenuBar(self.menubar)
		self.menubar.Bind()

		self.toolbar = BEEFToolBar(self)
		self.SetToolBar(self.toolbar)
		self.toolbar.Bind()
		self.toolbar.Realize()

		self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_LIVE_UPDATE)
		border = wx.BORDER_SUNKEN
		self.pane1 = wx.Window(self.splitter, style=border)
		self.pane2 = wx.Window(self.splitter, style=border)
		self.splitter.SetMinimumPaneSize(50)
		self.splitter.SplitVertically(self.pane1, self.pane2, 250)

		self.treectrl = BEEFTreeCtrl(self, self.pane1)
		self.treectrl.reset()
		self.treectrl.Bind()

		self.notebook = BEEFNotebook(self, self.pane2)
		self.sizer = wx.BoxSizer()
		self.sizer.Add(self.notebook, 1, wx.EXPAND)
		self.pane2.SetSizer(self.sizer)

		self.editDialogs = []
		for t in self.resourceTypes:
			ed = BEEFEditDialog(self, t[0], None)
			self.editDialogs.append(ed)

		self.tmpDir = tempfile.mkdtemp(prefix="beef-")
		self.projectFilename = ""
		self.setUnsaved(False)

		if "watchdog" in sys.modules:
			self.fileHandler = BEEFFileHandler(self)
			self.observer = Observer()
			self.observer.schedule(self.fileHandler, self.tmpDir, recursive=True)

		self.new()
		if file:
			self.load(file)
		else:
			self.SetStatusText("BEEF Loaded")

		try:
			if "watchdog" in sys.modules:
				self.observer.start()
		except OSError:
			print("Failed to get observers for resources, they will not automatically update")

		self.Show(True)
	def Close(self):
		self.quit(None)
	def quit(self, event):
		if not self.confirmClose():
			return

		try:
			if "watchdog" in sys.modules:
				self.observer.stop()
				self.observer.join()
		except RuntimeError:
			pass

		try:
			# "/cfg" and "/resources" will not be removed when the project is closed if the user closes the program with the window manager, e.g. Alt-F4
			if os.path.isfile(self.tmpDir + "/config.json"):
				os.remove(self.tmpDir + "/config.json")
			if os.path.isdir(self.tmpDir+"/cfg"):
				shutil.rmtree(self.tmpDir + "/cfg")
			if os.path.isdir(self.tmpDir+"/resources"):
				shutil.rmtree(self.tmpDir + "/resources")
			os.rmdir(self.tmpDir)
		except OSError:
			print("Failed to remove temporary directory \"" + self.tmpDir + "\"")

		self.Destroy()

	def getDir(self):
		return os.path.dirname(os.path.realpath(__file__))
	def log(self, string):
		print(string)

	def getVersionString(self):
		return str(BEEF_VERSION_MAJOR) + "." + str(BEEF_VERSION_MINOR) + "." + str(BEEF_VERSION_RELEASE)
	def ShowAbout(self):
		info = wx.adv.AboutDialogInfo()
		info.SetName("BasicEventEngine Frontend")
		info.SetVersion("v" + self.getVersionString())
		info.SetCopyright("(c) 2017 Luke Montalvo <lukemontalvo@gmail.com>")
		info.SetDescription(
			"BEEF is the graphical editor for the BasicEventEngine, an OpenGL game engine written in C++.\n\n"
			"The entire project is under heavy development so please report all bugs to Luke! :)"
		)
		info.SetWebSite("https://github.com/piluke/BasicEventEngineFrontend")

		l = ""
		try :
			with open("LICENSE", "r") as f:
				l = f.read()
		except IOError:
			l = "LICENSE file not found, a copy is available at https://mitlicense.org/"
		info.License = l

		wx.adv.AboutBox(info)

	def load(self, filename):
		if not self.confirmClose():
			return

		self.ready = False
		self.projectFilename = filename

		self.log("Loading \"" + self.projectFilename + "\"...")

		self.compiler.clean()

		with tarfile.open(self.projectFilename, "r:gz") as tar:
			tar.extractall(self.tmpDir)

		try:
			self._deserialize()
		except IOError:
			self.log("Failed to deserialize resources during load!")
			self.SetStatusText("Failed to deserialize resources during load!")
			return

		self.treectrl.expandRoot()

		resources = itertools.chain(
			self.sprites, self.sounds, self.backgrounds,
			self.fonts, self.paths, self.timelines,
			self.meshes, self.lights, self.objects, self.rooms
		)
		orl = self.gameCfg["open_resources"]
		self.gameCfg["open_resources"] = []
		for res in orl:
			for r in resources:
				if res == r.name:
					r.initPage()
					break

		for i in range(len(self.editDialogs)):
			self.editDialogs[i].setProgram(self.gameCfg["resource_edit_programs"][i])

		self.treectrl.SetFocus()
		self.treectrl.SetFocusedItem(self.treectrl.rootList[0])

		self.setUnsaved(False)
		self.SetStatusText("Loaded \"" + self.projectFilename + "\"!")
		self.ready = True
	def _deserialize(self):
		with open(self.tmpDir+"/config.json", "r") as f:
			self.gameCfg = json.loads(f.read())
		self.gameCfg["resource_edit_programs"] = {int(k):v for k,v in self.gameCfg["resource_edit_programs"].items()} # Convert int keys from JSON strings
		for fn in glob.glob(self.tmpDir+"/resources/sprites/*.json"):
			with open(fn, "r") as f:
				r = BEEFSprite(self, None)
				r.deserialize(f.read())
				self.addSprite(r.name, r)
		for fn in glob.glob(self.tmpDir+"/resources/sounds/*.json"):
			with open(fn, "r") as f:
				r = BEEFSound(self, None)
				r.deserialize(f.read())
				self.addSound(r.name, r)
		for fn in glob.glob(self.tmpDir+"/resources/backgrounds/*.json"):
			with open(fn, "r") as f:
				r = BEEFBackground(self, None)
				r.deserialize(f.read())
				self.addBackground(r.name, r)
		for fn in glob.glob(self.tmpDir+"/resources/fonts/*.json"):
			with open(fn, "r") as f:
				r = BEEFFont(self, None)
				r.deserialize(f.read())
				self.addFont(r.name, r)
		for fn in glob.glob(self.tmpDir+"/resources/paths/*.json"):
			with open(fn, "r") as f:
				r = BEEFPath(self, None)
				r.deserialize(f.read())
				self.addPath(r.name, r)
		for fn in glob.glob(self.tmpDir+"/resources/timelines/*.json"):
			with open(fn, "r") as f:
				r = BEEFTimeline(self, None)
				r.deserialize(f.read())
				self.addTimeline(r.name, r)
		for fn in glob.glob(self.tmpDir+"/resources/meshes/*.json"):
			with open(fn, "r") as f:
				r = BEEFMesh(self, None)
				r.deserialize(f.read())
				self.addMesh(r.name, r)
		for fn in glob.glob(self.tmpDir+"/resources/lights/*.json"):
			with open(fn, "r") as f:
				r = BEEFLight(self, None)
				r.deserialize(f.read())
				self.addLight(r.name, r)
		for fn in glob.glob(self.tmpDir+"/resources/objects/*.json"):
			with open(fn, "r") as f:
				r = BEEFObject(self, None)
				r.deserialize(f.read())
				self.addObject(r.name, r)
		for fn in glob.glob(self.tmpDir+"/resources/rooms/*.json"):
			with open(fn, "r") as f:
				r = BEEFRoom(self, None)
				r.deserialize(f.read())
				self.addRoom(r.name, r)

	def setUnsaved(self, s=True):
		self._unsaved = s

		filename = self.projectFilename
		if filename == "":
			filename = "New"

		if self._unsaved:
			self.SetTitle("*" + os.path.basename(filename) + " - BEE Frontend v" + self.getVersionString())
		else:
			self.SetTitle(os.path.basename(filename) + " - BEE Frontend v" + self.getVersionString())
	def save(self, filename=None):
		if filename:
			self.projectFilename = filename
			self.setUnsaved()

		if self.projectFilename == "":
			self.log("Failed to save, empty filename")
			return

		if not self._unsaved:
			return

		self.log("Saving \"" + self.projectFilename + "\"...")

		resources = itertools.chain(
			self.sprites, self.sounds, self.backgrounds,
			self.fonts, self.paths, self.timelines,
			self.meshes, self.lights, self.objects, self.rooms
		)
		for r in resources:
			if r:
				r.commitPage()

		for i in range(len(self.editDialogs)):
			if self.editDialogs[i].text.GetValue() == self.editDialogs[i].getDefault():
				self.gameCfg["resource_edit_programs"][i] = ""
			else:
				self.gameCfg["resource_edit_programs"][i] = self.editDialogs[i].text.GetValue()

		try:
			self._serialize()
		except IOError:
			self.log("Failed to serialize resources during save!")
			self.SetStatusText("Failed to serialize resources during save!")
			return

		with tarfile.open(self.projectFilename, "w:gz") as tar:
			for d in ["/cfg", "/resources", "/config.json"]:
				tar.add(self.tmpDir+d, arcname=os.path.basename(self.tmpDir+d))

		self.setUnsaved(False)
		self.SetStatusText("Saved \"" + self.projectFilename + "\"!")
	def _serialize(self):
		with open(self.tmpDir+"/config.json", "w") as f:
			f.write(json.dumps(self.gameCfg, indent=4))

		for r in self.sprites:
			if r:
				with open(self.tmpDir+"/resources/sprites/" + r.name + ".json", "w") as f:
					f.write(r.serialize())
		for r in self.sounds:
			if r:
				with open(self.tmpDir+"/resources/sounds/" + r.name + ".json", "w") as f:
					f.write(r.serialize())
		for r in self.backgrounds:
			if r:
				with open(self.tmpDir+"/resources/backgrounds/" + r.name + ".json", "w") as f:
					f.write(r.serialize())
		for r in self.fonts:
			if r:
				with open(self.tmpDir+"/resources/fonts/" + r.name + ".json", "w") as f:
					f.write(r.serialize())
		for r in self.paths:
			if r:
				with open(self.tmpDir+"/resources/paths/" + r.name + ".json", "w") as f:
					f.write(r.serialize())
		for r in self.timelines:
			if r:
				with open(self.tmpDir+"/resources/timelines/" + r.name + ".json", "w") as f:
					f.write(r.serialize())
		for r in self.meshes:
			if r:
				with open(self.tmpDir+"/resources/meshes/" + r.name + ".json", "w") as f:
					f.write(r.serialize())
		for r in self.lights:
			if r:
				with open(self.tmpDir+"/resources/lights/" + r.name + ".json", "w") as f:
					f.write(r.serialize())
		for r in self.objects:
			if r:
				with open(self.tmpDir+"/resources/objects/" + r.name + ".json", "w") as f:
					f.write(r.serialize())
		for r in self.rooms:
			if r:
				with open(self.tmpDir+"/resources/rooms/" + r.name + ".json", "w") as f:
					f.write(r.serialize())
	def confirmOverwriteResource(self, fn, name):
		dialog = wx.MessageDialog(
			self, "Another resource has the name \"" + name + "\". Overwrite it?",
			"Resource Name Conflict",
			wx.YES_NO | wx.ICON_QUESTION
		)

		if dialog.ShowModal() == wx.ID_NO:
			dialog.Destroy()
			return False

		dialog.Destroy()
		return True
	def dialogRename(self, name):
		dialog = wx.TextEntryDialog(
			self, "Another resource has the name \"" + name + "\". Please enter a different name for the selected resource:",
			"Resource Name Conflict"
		)
		dialog.SetValue(name)

		if dialog.ShowModal() == wx.ID_OK:
			return dialog.GetValue()

		return None

	def confirmClose(self):
		if self._unsaved:
			dialog = wx.MessageDialog(
				self, "Save before closing?",
				"Unsaved Changes",
				wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION
			)
			v = dialog.ShowModal()

			if v == wx.ID_YES:
				self.menubar.MenuFileSave(None)
				if self._unsaved:
					dialog.Destroy()
					return False
			elif v == wx.ID_NO:
				pass
			else:
				dialog.Destroy()
				return False
			dialog.Destroy()

		shutil.rmtree(self.tmpDir + "/cfg")
		shutil.rmtree(self.tmpDir + "/resources")
		os.remove(self.tmpDir + "/config.json")

		self.projectFilename = ""

		resources = itertools.chain(
			self.sprites, self.sounds, self.backgrounds,
			self.fonts, self.paths, self.timelines,
			self.meshes, self.lights, self.objects, self.rooms
		)
		for r in resources:
			if r:
				r.destroyPage(isClosing=True)
		self.notebook.DeleteAllPages()

		self.sprites = []
		self.sounds = []
		self.backgrounds = []
		self.fonts = []
		self.paths = []
		self.timelines = []
		self.meshes = []
		self.lights = []
		self.objects = []
		self.rooms = []

		self.treectrl.reset()

		self.SetStatusText("Project closed")
		return True
	def new(self):
		self.projectFilename = ""

		self.gameCfg = {
			"beef_version_major": BEEF_VERSION_MAJOR,
			"beef_version_minor": BEEF_VERSION_MINOR,
			"beef_version_release": BEEF_VERSION_RELEASE,

			"game_name": "BEE_Example",

			"game_version_major": 0,
			"game_version_minor": 0,
			"game_version_release": 1,

			"open_resources": [],

			"resource_edit_programs": {
				0: "", 1: "", 2: "", 3: "", 4: "",
				5: "", 6: "", 7: "", 8: "", 9: ""
			}
		}
		with open(self.tmpDir+"/config.json", "w") as f:
			f.write(json.dumps(self.gameCfg, indent=4))

		os.mkdir(self.tmpDir + "/cfg")
		os.mkdir(self.tmpDir + "/resources")
		for t in self.resourceTypes:
			os.mkdir(self.tmpDir + "/resources/" + t[1].lower())

		self.setUnsaved(False)
		self.SetTitle("New - BEE Frontend v" + self.getVersionString())
		self.SetStatusText("New project created")
		self.ready = True

	def getNextGid(self):
		return (
			len(self.sprites) +
			len(self.sounds) +
			len(self.backgrounds) +
			len(self.fonts) +
			len(self.paths) +
			len(self.timelines) +
			len(self.meshes) +
			len(self.lights) +
			len(self.objects) +
			len(self.rooms)
		)
	def addSprite(self, name, resource=None):
		r = resource
		if not r:
			r = BEEFSprite(self, name)

		r.id = len(self.sprites)
		r.gid = self.getNextGid()
		r.resourceList = self.sprites

		while not r.checkName(name, shouldDelete=False):
			name = self.dialogRename(name)

			if not name:
				return (None, None)

		self.setUnsaved()
		r.name = name

		self.sprites.append(r)
		i = self.treectrl.addSprite(name, r)
		r.treeitem = i

		return (r, i)
	def addSound(self, name, resource=None):
		r = resource
		if not r:
			r = BEEFSound(self, name)

		r.id = len(self.sounds)
		r.gid = self.getNextGid()
		r.resourceList = self.sounds

		while not r.checkName(name, shouldDelete=False):
			name = self.dialogRename(name)

			if not name:
				return (None, None)

		self.setUnsaved()
		r.name = name

		self.sounds.append(r)
		i = self.treectrl.addSound(name, r)
		r.treeitem = i

		return (r, i)
	def addBackground(self, name, resource=None):
		r = resource
		if not r:
			r = BEEFBackground(self, name)

		r.id = len(self.backgrounds)
		r.gid = self.getNextGid()
		r.resourceList = self.backgrounds

		while not r.checkName(name, shouldDelete=False):
			name = self.dialogRename(name)

			if not name:
				return (None, None)

		self.setUnsaved()
		r.name = name

		self.backgrounds.append(r)
		i = self.treectrl.addBackground(name, r)
		r.treeitem = i

		return (r, i)
	def addFont(self, name, resource=None):
		r = resource
		if not r:
			r = BEEFFont(self, name)

		r.id = len(self.fonts)
		r.gid = self.getNextGid()
		r.resourceList = self.fonts

		while not r.checkName(name, shouldDelete=False):
			name = self.dialogRename(name)

			if not name:
				return (None, None)

		self.setUnsaved()
		r.name = name

		self.fonts.append(r)
		i = self.treectrl.addFont(name, r)
		r.treeitem = i

		return (r, i)
	def addPath(self, name, resource=None):
		r = resource
		if not r:
			r = BEEFPath(self, name)

		r.id = len(self.paths)
		r.gid = self.getNextGid()
		r.resourceList = self.paths

		while not r.checkName(name, shouldDelete=False):
			name = self.dialogRename(name)

			if not name:
				return (None, None)

		self.setUnsaved()
		r.name = name

		self.paths.append(r)
		i = self.treectrl.addPath(name, r)
		r.treeitem = i

		return (r, i)
	def addTimeline(self, name, resource=None):
		r = resource
		if not r:
			r = BEEFTimeline(self, name)

		r.id = len(self.timelines)
		r.gid = self.getNextGid()
		r.resourceList = self.timelines

		while not r.checkName(name, shouldDelete=False):
			name = self.dialogRename(name)

			if not name:
				return (None, None)

		self.setUnsaved()
		r.name = name

		self.timelines.append(r)
		i = self.treectrl.addTimeline(name, r)
		r.treeitem = i

		return (r, i)
	def addMesh(self, name, resource=None):
		r = resource
		if not r:
			r = BEEFMesh(self, name)

		r.id = len(self.meshes)
		r.gid = self.getNextGid()
		r.resourceList = self.meshes

		while not r.checkName(name, shouldDelete=False):
			name = self.dialogRename(name)

			if not name:
				return (None, None)

		self.setUnsaved()
		r.name = name

		self.meshes.append(r)
		i = self.treectrl.addMesh(name, r)
		r.treeitem = i

		return (r, i)
	def addLight(self, name, resource=None):
		r = resource
		if not r:
			r = BEEFLight(self, name)

		r.id = len(self.lights)
		r.gid = self.getNextGid()
		r.resourceList = self.lights

		while not r.checkName(name, shouldDelete=False):
			name = self.dialogRename(name)

			if not name:
				return (None, None)

		self.setUnsaved()
		r.name = name

		self.lights.append(r)
		i = self.treectrl.addLight(name, r)
		r.treeitem = i

		return (r, i)
	def addObject(self, name, resource=None):
		r = resource
		if not r:
			r = BEEFObject(self, name)

		r.id = len(self.objects)
		r.gid = self.getNextGid()
		r.resourceList = self.objects

		while not r.checkName(name, shouldDelete=False):
			name = self.dialogRename(name)

			if not name:
				return (None, None)

		self.setUnsaved()
		r.name = name

		self.objects.append(r)
		i = self.treectrl.addObject(name, r)
		r.treeitem = i

		return (r, i)
	def addRoom(self, name, resource=None):
		r = resource
		if not r:
			r = BEEFRoom(self, name)

		r.id = len(self.rooms)
		r.gid = self.getNextGid()
		r.resourceList = self.rooms

		while not r.checkName(name, shouldDelete=False):
			name = self.dialogRename(name)

			if not name:
				return (None, None)

		self.setUnsaved()
		r.name = name

		self.rooms.append(r)
		i = self.treectrl.addRoom(name, r)
		r.treeitem = i

		return (r, i)

	def adjustIndices(self, index):
		if index < 0:
			return

		resources = itertools.chain(
			self.sprites, self.sounds, self.backgrounds,
			self.fonts, self.paths, self.timelines,
			self.meshes, self.lights, self.objects, self.rooms
		)
		for r in resources:
			if r.pageIndex > index:
				r.pageIndex -= 1

	def getResourceFromPath(self, path):
		roots = [
			"/resources/sprites/",
			"/resources/sounds/",
			"/resources/backgrounds/",
			"/resources/fonts/",
			"/resources/paths/",
			"/resources/timelines/",
			"/resources/meshes/",
			"/resources/lights/",
			"/resources/objects/",
			"/resources/rooms/"
		]
		rlists = [
			self.sprites,
			self.sounds,
			self.backgrounds,
			self.fonts,
			self.paths,
			self.timelines,
			self.meshes,
			self.lights,
			self.objects,
			self.rooms
		]

		i = 0
		for root in roots:
			if path.startswith(root):
				for r in rlists[i]:
					if path == root+r.name+".json" or path == r.properties["path"]:
						return rlists[i][r.id]
				else:
					return None
			i += 1

		return None
	def editResource(self, resource):
		p = self.editDialogs[resource.type].show()
		if p:
			if resource.properties["path"]:
				subprocess.Popen([p, self.tmpDir+resource.properties["path"]])
				return True

		return False
	def enqueue(self, func):
		self.callbackQueue.put(func)
	def dequeue(self):
		while True:
			try:
				callback = self.callbackQueue.get()
			except Queue.Empty:
				break
			callback()

if __name__ == "__main__":
	file = None
	if len(sys.argv) > 1:
		file = sys.argv[1]

	app = wx.App()
	frame = BEEFFrame(None, -1, file)
	app.MainLoop()
