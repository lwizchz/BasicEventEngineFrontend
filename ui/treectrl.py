# Copyright (c) 2017-18 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEEF.
# BEEF is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

import os
import shutil

from resources.enum import EResource

class BEEFTreeCtrl(wx.TreeCtrl):
	def __init__(self, top, parent):
		wx.TreeCtrl.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, wx.TR_HAS_BUTTONS | wx.TR_EDIT_LABELS | wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT)
		self.top = top
		self.parent = parent

		self.parent.Bind(wx.EVT_SIZE, self.OnSize)

		size = (16,16)
		self.il = wx.ImageList(size[0], size[1])
		self.iconFolder = self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, size))
		self.iconFolderOpen = self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, size))
		self.iconFile = self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, size))
		self.SetImageList(self.il)

		self.root = self.AddRoot("Resources")
		self.SetItemImage(self.root, self.iconFolder, wx.TreeItemIcon_Normal)
		self.SetItemImage(self.root, self.iconFolderOpen, wx.TreeItemIcon_Expanded)

		self.rootList = []
		def addTree(name, data):
			c = self.AppendItem(self.root, name)
			self.SetItemData(c, data)

			self.SetItemImage(c, self.iconFolder, wx.TreeItemIcon_Normal)
			self.SetItemImage(c, self.iconFolderOpen, wx.TreeItemIcon_Expanded)

			self.rootList.append(c)

		for r in EResource.getAll():
			addTree(EResource.getPlural(r), EResource.get(r))

		self.SetItemData(self.AppendItem(self.root, "-"*15), None)
		addTree("Configs", None)
		addTree("Extras", None)

	def reset(self):
		for r in self.rootList:
			self.DeleteChildren(r)

	def Bind(self):
		self.parent.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginEdit, self)
		self.parent.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndEdit, self)
		self.parent.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate, self)
		self.parent.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.ShowCMenu, self)

		# Bind context menu actions
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootTextureCreate, id=1001)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootTextureExpand, id=1002)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootTextureCollapse, id=1003)

		self.parent.Bind(wx.EVT_MENU, self.CMenuRootSoundCreate, id=1011)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootSoundExpand, id=1012)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootSoundCollapse, id=1013)

		self.parent.Bind(wx.EVT_MENU, self.CMenuRootFontCreate, id=1021)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootFontExpand, id=1022)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootFontCollapse, id=1023)

		self.parent.Bind(wx.EVT_MENU, self.CMenuRootPathCreate, id=1031)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootPathExpand, id=1032)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootPathCollapse, id=1033)

		self.parent.Bind(wx.EVT_MENU, self.CMenuRootTimelineCreate, id=1041)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootTimelineExpand, id=1042)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootTimelineCollapse, id=1043)

		self.parent.Bind(wx.EVT_MENU, self.CMenuRootMeshCreate, id=1051)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootMeshExpand, id=1052)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootMeshCollapse, id=1053)

		self.parent.Bind(wx.EVT_MENU, self.CMenuRootLightCreate, id=1061)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootLightExpand, id=1062)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootLightCollapse, id=1063)

		self.parent.Bind(wx.EVT_MENU, self.CMenuRootObjectCreate, id=1071)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootObjectExpand, id=1072)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootObjectCollapse, id=1073)

		self.parent.Bind(wx.EVT_MENU, self.CMenuRootRoomCreate, id=1081)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootRoomExpand, id=1082)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootRoomCollapse, id=1083)

		self.parent.Bind(wx.EVT_MENU, self.CMenuRootConfigCreate, id=1091)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootConfigImport, id=1092)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootConfigExpand, id=1093)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootConfigCollapse, id=1094)

		self.parent.Bind(wx.EVT_MENU, self.CMenuRootExtraCreate, id=1101)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootExtraImport, id=1102)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootExtraExpand, id=1103)
		self.parent.Bind(wx.EVT_MENU, self.CMenuRootExtraCollapse, id=1104)

		# Bind resource context menu actions
		self.top.Bind(wx.EVT_MENU, self.CMenuResourceOpen, id=10001)
		self.top.Bind(wx.EVT_MENU, self.CMenuResourceCreate, id=10002)
		self.top.Bind(wx.EVT_MENU, self.CMenuResourceRename, id=10003)
		self.top.Bind(wx.EVT_MENU, self.CMenuResourceDelete, id=10004)
		self.top.Bind(wx.EVT_MENU, self.CMenuResourceDuplicate, id=10005)
		self.top.Bind(wx.EVT_MENU, self.CMenuRoomSetAsFirst, id=10006)
		accelTable = wx.AcceleratorTable([
			(wx.ACCEL_NORMAL, wx.WXK_RETURN, 10001),
			(wx.ACCEL_NORMAL, wx.WXK_F2, 10003),
			(wx.ACCEL_NORMAL, wx.WXK_DELETE, 10004),
			(wx.ACCEL_ALT, wx.WXK_INSERT, 10005)
		])
		self.SetAcceleratorTable(accelTable)

	def OnSize(self, event):
		w, h = self.parent.GetClientSize()
		self.SetSize(0, 0, w, h)

	def OnBeginEdit(self, event):
		item = event.GetItem()
		if item in self.rootList or not self.GetItemData(item):
			event.Veto()
	def OnEndEdit(self, event):
		item = event.GetItem()
		if not item in self.rootList:
			r = self.GetItemData(item)

			if r:
				l = event.GetLabel()
				if r.name == l or event.IsEditCancelled():
					return

				if not r.rename(l):
					event.Veto()
					return
				self.top.setUnsaved()
	def OnActivate(self, event):
		item = event.GetItem()
		if item in self.rootList:
			self.Toggle(item)
		else:
			r = self.GetItemData(item)
			if r:
				r.MenuOpen(None)
	def expandRoot(self):
		for rt in self.rootList:
			self.Expand(rt)

	def ShowCMenu(self, event):
		item = event.GetItem()
		self.cmenu = wx.Menu()

		if item in self.rootList:
			t = self.GetItemData(item)

			for i in range(EResource._MAX):
				if t == EResource.get(i):
					self.cmenu.Append(1001+i*10, "Create new "+EResource.get(i))
					self.cmenu.Append(1002+i*10, "Expand all "+EResource.getPlural(i))
					self.cmenu.Append(1003+i*10, "Collapse all "+EResource.getPlural(i))
					break;
			else: # Show Configs/Extras CMenu
				rt = self.GetItemText(item)
				if rt == "Configs":
					self.cmenu.Append(1091, "Create new Config File")
					self.cmenu.Append(1092, "Import new Config File")
					self.cmenu.Append(1093, "Expand all Config Files")
					self.cmenu.Append(1094, "Collapse all Config Files")
				elif rt == "Extras":
					self.cmenu.Append(1101, "Create new Extra File")
					self.cmenu.Append(1102, "Import new Extra File")
					self.cmenu.Append(1103, "Expand all Extra Files")
					self.cmenu.Append(1104, "Collapse all Extra Files")
				else:
					raise RuntimeError("Invalid resource type: {}".format(rt))
		else:
			r = self.GetItemData(item)
			if r:
				self.cmenu.Append(10001, "Open properties\tEnter")
				self.cmenu.Append(10002, "Create new " + EResource.get(r.type))
				self.cmenu.Append(10003, "Rename \"" + r.name + "\"\tF2")
				self.cmenu.Append(10004, "Delete \"" + r.name + "\"\tDelete")
				self.cmenu.Append(10005, "Duplicate\tAlt+Insert")
				if r.type == EResource.ROOM:
					self.cmenu.Append(10006, "Set as the first room")
			else:
				self.cmenu.Destroy()
				return

		self.PopupMenu(self.cmenu)
		self.cmenu.Destroy()

	def addTexture(self, name, resource):
		item = self.AppendItem(self.rootList[EResource.TEXTURE], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addSound(self, name, resource):
		item = self.AppendItem(self.rootList[EResource.SOUND], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addFont(self, name, resource):
		item = self.AppendItem(self.rootList[EResource.FONT], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addPath(self, name, resource):
		item = self.AppendItem(self.rootList[EResource.PATH], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addTimeline(self, name, resource):
		item = self.AppendItem(self.rootList[EResource.TIMELINE], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addMesh(self, name, resource):
		item = self.AppendItem(self.rootList[EResource.MESH], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addLight(self, name, resource):
		item = self.AppendItem(self.rootList[EResource.LIGHT], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addObject(self, name, resource):
		item = self.AppendItem(self.rootList[EResource.OBJECT], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addRoom(self, name, resource):
		item = self.AppendItem(self.rootList[EResource.ROOM], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		if resource.name == self.top.gameCfg["first_room"]:
			self.SetItemBold(item, True)

		return item
	def addConfig(self, name, resource):
		item = self.AppendItem(self.rootList[9], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addExtra(self, name, resource):
		item = self.AppendItem(self.rootList[10], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item

	def CMenuRootTextureCreate(self, event):
		name = "spr_" + str(len(self.top.textures))
		_, item = self.top.addTexture(name)

		if item:
			self.CMenuRootTextureExpand(None)
			self.SelectItem(item)
	def CMenuRootTextureExpand(self, event):
		self.Expand(self.rootList[EResource.TEXTURE])
	def CMenuRootTextureCollapse(self, event):
		self.Collapse(self.rootList[EResource.TEXTURE])

	def CMenuRootSoundCreate(self, event):
		name = "snd_" + str(len(self.top.sounds))
		_, item = self.top.addSound(name)

		if item:
			self.CMenuRootSoundExpand(None)
			self.SelectItem(item)
	def CMenuRootSoundExpand(self, event):
		self.Expand(self.rootList[EResource.SOUND])
	def CMenuRootSoundCollapse(self, event):
		self.Collapse(self.rootList[EResource.SOUND])

	def CMenuRootFontCreate(self, event):
		name = "font_" + str(len(self.top.fonts))
		_, item = self.top.addFont(name)

		if item:
			self.CMenuRootFontExpand(None)
			self.SelectItem(item)
	def CMenuRootFontExpand(self, event):
		self.Expand(self.rootList[EResource.FONT])
	def CMenuRootFontCollapse(self, event):
		self.Collapse(self.rootList[EResource.FONT])

	def CMenuRootPathCreate(self, event):
		name = "path_" + str(len(self.top.paths))
		_, item = self.top.addPath(name)

		if item:
			self.CMenuRootPathExpand(None)
			self.SelectItem(item)
	def CMenuRootPathExpand(self, event):
		self.Expand(self.rootList[EResource.PATH])
	def CMenuRootPathCollapse(self, event):
		self.Collapse(self.rootList[EResource.PATH])

	def CMenuRootTimelineCreate(self, event):
		name = "tl_" + str(len(self.top.timelines))
		_, item = self.top.addTimeline(name)

		if item:
			self.CMenuRootTimelineExpand(None)
			self.SelectItem(item)
	def CMenuRootTimelineExpand(self, event):
		self.Expand(self.rootList[EResource.TIMELINE])
	def CMenuRootTimelineCollapse(self, event):
		self.Collapse(self.rootList[EResource.TIMELINE])

	def CMenuRootMeshCreate(self, event):
		name = "mesh_" + str(len(self.top.meshes))
		_, item = self.top.addMesh(name)

		if item:
			self.CMenuRootMeshExpand(None)
			self.SelectItem(item)
	def CMenuRootMeshExpand(self, event):
		self.Expand(self.rootList[EResource.MESH])
	def CMenuRootMeshCollapse(self, event):
		self.Collapse(self.rootList[EResource.MESH])

	def CMenuRootLightCreate(self, event):
		name = "lt_" + str(len(self.top.lights))
		_, item = self.top.addLight(name)

		if item:
			self.CMenuRootLightExpand(None)
			self.SelectItem(item)
	def CMenuRootLightExpand(self, event):
		self.Expand(self.rootList[EResource.LIGHT])
	def CMenuRootLightCollapse(self, event):
		self.Collapse(self.rootList[EResource.LIGHT])

	def CMenuRootObjectCreate(self, event):
		name = "obj_" + str(len(self.top.objects))
		_, item = self.top.addObject(name)

		if item:
			self.CMenuRootObjectExpand(None)
			self.SelectItem(item)
	def CMenuRootObjectExpand(self, event):
		self.Expand(self.rootList[EResource.OBJECT])
	def CMenuRootObjectCollapse(self, event):
		self.Collapse(self.rootList[EResource.OBJECT])

	def CMenuRootRoomCreate(self, event):
		name = "rm_" + str(len(self.top.rooms))
		_, item = self.top.addRoom(name)

		if item:
			self.CMenuRootRoomExpand(None)
			self.SelectItem(item)
	def CMenuRootRoomExpand(self, event):
		self.Expand(self.rootList[EResource.ROOM])
	def CMenuRootRoomCollapse(self, event):
		self.Collapse(self.rootList[EResource.ROOM])

	def CMenuRootConfigCreate(self, event):
		name = self.top.dialogRename("")
		if name:
			_, item = self.top.addConfig(name)

			if item:
				self.CMenuRootConfigExpand(None)
				self.SelectItem(item)
	def CMenuRootConfigImport(self, event):
		wildcards = (
			"Config File (*.cfg)|*.cfg|"
			"All files (*)|*"
		)

		dialog = wx.FileDialog(
			self.top, message="Import Config File",
			defaultDir=self.top.rootDir,
			wildcard=wildcards,
			style=wx.FD_OPEN
		)

		if dialog.ShowModal() == wx.ID_OK:
			path = dialog.GetPath()
			name = os.path.basename(path)

			r, item = self.top.addConfig(name, None)

			if item:
				shutil.copyfile(path, self.top.rootDir+r.path+r.name)
				r.update()

				self.CMenuRootConfigExpand(None)
				self.SelectItem(item)

		dialog.Destroy()
	def CMenuRootConfigExpand(self, event):
		self.Expand(self.rootList[9])
	def CMenuRootConfigCollapse(self, event):
		self.Collapse(self.rootList[9])

	def CMenuRootExtraCreate(self, event):
		name = self.top.dialogRename("")
		if name:
			_, item = self.top.addExtra(name)

			if item:
				self.CMenuRootExtraExpand(None)
				self.SelectItem(item)
	def CMenuRootExtraImport(self, event):
		wildcards = (
			"All files (*)|*"
		)

		dialog = wx.FileDialog(
			self.top, message="Import Extra File",
			defaultDir=self.top.rootDir,
			wildcard=wildcards,
			style=wx.FD_OPEN
		)

		if dialog.ShowModal() == wx.ID_OK:
			path = dialog.GetPath()
			name = os.path.basename(path)

			r, item = self.top.addExtra(name, None)

			if item:
				shutil.copyfile(path, self.top.rootDir+r.path+r.name)
				r.update()

				self.CMenuRootExtraExpand(None)
				self.SelectItem(item)

		dialog.Destroy()
	def CMenuRootExtraExpand(self, event):
		self.Expand(self.rootList[10])
	def CMenuRootExtraCollapse(self, event):
		self.Collapse(self.rootList[10])

	def CMenuResourceOpen(self, event):
		item = self.GetFocusedItem()
		if not item in self.rootList:
			r = self.GetItemData(item)
			if r:
				r.MenuOpen(event)
	def CMenuResourceCreate(self, event):
		item = self.GetFocusedItem()
		if not item in self.rootList:
			r = self.GetItemData(item)
			if r:
				creators = [
					self.CMenuRootTextureCreate, self.CMenuRootSoundCreate, self.CMenuRootFontCreate,
					self.CMenuRootPathCreate, self.CMenuRootTimelineCreate, self.CMenuRootMeshCreate,
					self.CMenuRootLightCreate, self.CMenuRootObjectCreate, self.CMenuRootRoomCreate,
					None, self.CMenuRootConfigCreate, self.CMenuRootExtraCreate
				]
				creators[r.type](None)
	def CMenuResourceRename(self, event):
		item = self.GetFocusedItem()
		if not item in self.rootList:
			r = self.GetItemData(item)
			if r:
				r.MenuRename(event)
	def CMenuResourceDelete(self, event):
		item = self.GetFocusedItem()
		if not item in self.rootList:
			r = self.GetItemData(item)
			if r:
				r.MenuDelete(event)
	def CMenuResourceDuplicate(self, event):
		item = self.GetFocusedItem()
		if not item in self.rootList:
			r = self.GetItemData(item)
			if r:
				r.MenuDuplicate(event)
	def CMenuRoomSetAsFirst(self, event):
		item = self.GetFocusedItem()
		if not item in self.rootList:
			r = self.GetItemData(item)
			if r:
				first_room = self.top.gameCfg["first_room"]
				if first_room:
					for rm in self.top.rooms:
						if first_room == rm.name:
							self.SetItemBold(rm.treeitem, False)
							break

				self.top.gameCfg["first_room"] = r.name
				self.SetItemBold(item, True)
				self.top.setUnsaved()
