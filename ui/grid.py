# Copyright (c) 2017-18 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEEF.
# BEEF is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

class BEEFGrid(wx.Panel):
	def __init__(self, parent, top, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.LC_ICON, scale=1):
		wx.Panel.__init__(self, parent, id, pos, size, style)
		self.SetBackgroundColour(wx.WHITE)

		self.top = top

		self.scale = scale
		self.object = None
		self.instances = []

		self.w = 0
		self.h = 0
		self.gridsize = 16

		self.Bind(wx.EVT_LEFT_UP, self.CreateInstance)
		self.Bind(wx.EVT_RIGHT_UP, self.DeleteInstance)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_PAINT, self.Redraw)

	def SetObject(self, object):
		self.object = object
	def AddInstance(self, inst):
		self.instances.append(inst)
	def SetDimensions(self, w, h):
		self.w = w
		self.h = h

	def GetEventPos(self, event):
		gx, gy = self.GetPosition()
		x = event.GetX()/self.scale
		y = event.GetY()/self.scale

		# Align to grid
		x = x//self.gridsize * self.gridsize
		y = y//self.gridsize * self.gridsize

		return (x, y)
	def CreateInstance(self, event):
		if not self.object:
			return

		x, y = self.GetEventPos(event)
		self.AddInstance((self.object, x, y, 0))
		self.top.setUnsaved()

		self.Redraw()
	def DeleteInstance(self, event):
		x, y = self.GetEventPos(event)
		for inst in list(self.instances):
			if inst[1] == x and inst[2] == y:
				self.instances.remove(inst)
				self.top.setUnsaved()
				break

		self.Redraw()
	def OnSize(self, event):
		self.Redraw()
	def Redraw(self, event=None):
		if not event:
			self.Refresh()
			self.Update()
			return

		dc = wx.PaintDC(self)
		dc.Clear()

		dc.SetLogicalScale(self.scale, self.scale)
		dc.SetLogicalOrigin(0, 0)

		# Draw gridlines
		gridlines = []
		for x in range(0, self.w, self.gridsize):
			gridlines.append((
				x, 0,
				x, self.h
			))
		for y in range(0, self.h, self.gridsize):
			gridlines.append((
				0, y,
				self.w, y
			))
		dc.SetPen(wx.Pen(wx.Colour(192, 192, 192), 1))
		dc.DrawLineList(gridlines)

		dc.SetPen(wx.Pen(wx.BLACK, 1))
		dc.DrawLineList([(0, 0, 0, self.h), (0, 0, self.w, 0)])

		# Draw the instances
		for inst in self.instances:
			objects = [o for o in self.top.objects if o.name == inst[0]]
			if not objects:
				continue

			sprites = [s.inputs["bmp_texture"].GetBitmap() for s in self.top.textures if s.name == objects[0].properties["sprite"] and s.properties["path"] and s.inputs["bmp_texture"]]
			if not sprites:
				sprites = [wx.Bitmap(self.top.images["nosprite"])]

			dc.DrawBitmap(sprites[0], inst[1], inst[2], True)
