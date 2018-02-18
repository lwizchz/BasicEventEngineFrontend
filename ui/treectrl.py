# Copyright (c) 2017-18 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEEF.
# BEEF is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

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
		for r in EResource.getAll():
			c = self.AppendItem(self.root, EResource.getPlural(r))
			self.SetItemData(c, EResource.get(r))

			self.SetItemImage(c, self.iconFolder, wx.TreeItemIcon_Normal)
			self.SetItemImage(c, self.iconFolderOpen, wx.TreeItemIcon_Expanded)

			self.rootList.append(c)

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

		# Bind resource context menu actions
		self.top.Bind(wx.EVT_MENU, self.CMenuResourceOpen, id=10001)
		self.top.Bind(wx.EVT_MENU, self.CMenuRootTextureCreate, id=10002)
		self.top.Bind(wx.EVT_MENU, self.CMenuResourceRename, id=10003)
		self.top.Bind(wx.EVT_MENU, self.CMenuResourceDelete, id=10004)
		self.top.Bind(wx.EVT_MENU, self.CMenuResourceDuplicate, id=10005)
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
		if item in self.rootList:
			event.Veto()
	def OnEndEdit(self, event):
		item = event.GetItem()
		if not item in self.rootList:
			r = self.GetItemData(item)

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
			r.MenuOpen(None)
	def expandRoot(self):
		for rt in self.rootList:
			self.Expand(rt)

	def ShowCMenu(self, event):
		item = event.GetItem()
		self.cmenu = wx.Menu()

		if item in self.rootList:
			t = self.GetItemData(item)
			rt = self.top.resourceTypes

			for i in range(len(rt)):
				if t == rt[i][0]:
					self.cmenu.Append(1001+i*10, "Create new "+rt[i][0])
					self.cmenu.Append(1002+i*10, "Expand all "+rt[i][1])
					self.cmenu.Append(1003+i*10, "Collapse all "+rt[i][1])
					break;
			else:
				raise RuntimeError("Invalid resource type")
		else:
			r = self.GetItemData(item)
			self.cmenu.Append(10001, "Open properties\tEnter")
			self.cmenu.Append(10002, "Create new " + self.top.resourceTypes[r.type][0])
			self.cmenu.Append(10003, "Rename \"" + r.name + "\"\tF2")
			self.cmenu.Append(10004, "Delete \"" + r.name + "\"\tDelete")
			self.cmenu.Append(10005, "Duplicate\tAlt+Insert")

		self.PopupMenu(self.cmenu)
		self.cmenu.Destroy()

	def addTexture(self, name, resource):
		item = self.AppendItem(self.rootList[0], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addSound(self, name, resource):
		item = self.AppendItem(self.rootList[1], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addFont(self, name, resource):
		item = self.AppendItem(self.rootList[2], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addPath(self, name, resource):
		item = self.AppendItem(self.rootList[3], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addTimeline(self, name, resource):
		item = self.AppendItem(self.rootList[4], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addMesh(self, name, resource):
		item = self.AppendItem(self.rootList[5], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addLight(self, name, resource):
		item = self.AppendItem(self.rootList[6], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addObject(self, name, resource):
		item = self.AppendItem(self.rootList[7], name)
		self.SetItemData(item, resource)

		self.SetItemImage(item, self.iconFile, wx.TreeItemIcon_Normal)

		return item
	def addRoom(self, name, resource):
		item = self.AppendItem(self.rootList[8], name)
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
		self.Expand(self.rootList[0])
	def CMenuRootTextureCollapse(self, event):
		self.Collapse(self.rootList[0])

	def CMenuRootSoundCreate(self, event):
		name = "snd_" + str(len(self.top.sounds))
		_, item = self.top.addSound(name)

		if item:
			self.CMenuRootSoundExpand(None)
			self.SelectItem(item)
	def CMenuRootSoundExpand(self, event):
		self.Expand(self.rootList[1])
	def CMenuRootSoundCollapse(self, event):
		self.Collapse(self.rootList[1])

	def CMenuRootFontCreate(self, event):
		name = "font_" + str(len(self.top.fonts))
		_, item = self.top.addFont(name)

		if item:
			self.CMenuRootFontExpand(None)
			self.SelectItem(item)
	def CMenuRootFontExpand(self, event):
		self.Expand(self.rootList[3])
	def CMenuRootFontCollapse(self, event):
		self.Collapse(self.rootList[3])

	def CMenuRootPathCreate(self, event):
		name = "path_" + str(len(self.top.paths))
		_, item = self.top.addPath(name)

		if item:
			self.CMenuRootPathExpand(None)
			self.SelectItem(item)
	def CMenuRootPathExpand(self, event):
		self.Expand(self.rootList[4])
	def CMenuRootPathCollapse(self, event):
		self.Collapse(self.rootList[4])

	def CMenuRootTimelineCreate(self, event):
		name = "tl_" + str(len(self.top.timelines))
		_, item = self.top.addTimeline(name)

		if item:
			self.CMenuRootTimelineExpand(None)
			self.SelectItem(item)
	def CMenuRootTimelineExpand(self, event):
		self.Expand(self.rootList[5])
	def CMenuRootTimelineCollapse(self, event):
		self.Collapse(self.rootList[5])

	def CMenuRootMeshCreate(self, event):
		name = "mesh_" + str(len(self.top.meshes))
		_, item = self.top.addMesh(name)

		if item:
			self.CMenuRootMeshExpand(None)
			self.SelectItem(item)
	def CMenuRootMeshExpand(self, event):
		self.Expand(self.rootList[6])
	def CMenuRootMeshCollapse(self, event):
		self.Collapse(self.rootList[6])

	def CMenuRootLightCreate(self, event):
		name = "lt_" + str(len(self.top.lights))
		_, item = self.top.addLight(name)

		if item:
			self.CMenuRootLightExpand(None)
			self.SelectItem(item)
	def CMenuRootLightExpand(self, event):
		self.Expand(self.rootList[7])
	def CMenuRootLightCollapse(self, event):
		self.Collapse(self.rootList[7])

	def CMenuRootObjectCreate(self, event):
		name = "obj_" + str(len(self.top.objects))
		_, item = self.top.addObject(name)

		if item:
			self.CMenuRootObjectExpand(None)
			self.SelectItem(item)
	def CMenuRootObjectExpand(self, event):
		self.Expand(self.rootList[8])
	def CMenuRootObjectCollapse(self, event):
		self.Collapse(self.rootList[8])

	def CMenuRootRoomCreate(self, event):
		name = "rm_" + str(len(self.top.rooms))
		_, item = self.top.addRoom(name)

		if item:
			self.CMenuRootRoomExpand(None)
			self.SelectItem(item)
	def CMenuRootRoomExpand(self, event):
		self.Expand(self.rootList[9])
	def CMenuRootRoomCollapse(self, event):
		self.Collapse(self.rootList[9])

	def CMenuResourceOpen(self, event):
		item = self.GetFocusedItem()
		if not item in self.rootList:
			r = self.GetItemData(item)
			r.MenuOpen(event)
	def CMenuResourceRename(self, event):
		item = self.GetFocusedItem()
		if not item in self.rootList:
			r = self.GetItemData(item)
			r.MenuRename(event)
	def CMenuResourceDelete(self, event):
		item = self.GetFocusedItem()
		if not item in self.rootList:
			r = self.GetItemData(item)
			r.MenuDelete(event)
	def CMenuResourceDuplicate(self, event):
		item = self.GetFocusedItem()
		if not item in self.rootList:
			r = self.GetItemData(item)
			r.MenuDuplicate(event)
