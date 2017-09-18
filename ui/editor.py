# Copyright (c) 2017 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEE.
# BEE is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

import wx.stc

import math

class BEEFEditor(wx.stc.StyledTextCtrl):
	def __init__(self, top, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.LC_ICON, scale=2):
		wx.stc.StyledTextCtrl.__init__(self, parent, id, pos, size, style)

		self.top = top
		self.indent = 4

		self.SetLexer(wx.stc.STC_LEX_CPP)

		self.Colourise(0, -1)

		self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
		self.UpdateMargins()

		# Colors based on the Atom One Dark Syntax theme
		mono0 = "#282a2e"
		mono1 = "#9ca4b5"
		mono2 = "#80848c"
		mono3 = "#5c5f66"
		cyan = "#4a858c"
		blue = "#1e6aa8"
		purple = "#9344ab"
		green = "#7b9e62"
		red1 = "#a63a43"
		red2 = "#824944"
		orange1 = "#9c7048"
		orange2 = "#b0873a"

		font = "Courier New"
		size = 12
		fs = "face:{},size:{}".format(font, size)
		bfs = "back:{},{}".format(mono0, fs)
		self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT,     "fore:{},{}".format(mono1, bfs))

		self.StyleClearAll()
		self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT,     "fore:{},{}".format(mono1, bfs))
		self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER,  "fore:#000000,back:#C0C0C0,{}".format(fs))
		self.StyleSetSpec(wx.stc.STC_STYLE_CONTROLCHAR, "face:{}".format(font))
		self.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
		self.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")

		# C++ lexer colors
		self.StyleSetSpec(wx.stc.STC_C_DEFAULT, "fore:{},{}".format(mono1, fs))
		self.StyleSetSpec(wx.stc.STC_C_PREPROCESSOR, "fore:{},{}".format(purple, fs))
		self.StyleSetSpec(wx.stc.STC_C_IDENTIFIER, "fore:{},{}".format(blue, fs))
		self.StyleSetSpec(wx.stc.STC_C_STRING, "fore:{},{}".format(green, fs))
		self.StyleSetSpec(wx.stc.STC_C_NUMBER, "fore:{},{}".format(orange1, fs))
		self.StyleSetSpec(wx.stc.STC_C_CHARACTER, "fore:{},{}".format(mono1, fs))
		self.StyleSetSpec(wx.stc.STC_C_WORD, "fore:{},{}".format(purple, fs))
		self.StyleSetSpec(wx.stc.STC_C_WORD2, "fore:{},{}".format(purple, fs))
		self.StyleSetSpec(wx.stc.STC_C_OPERATOR, "fore:{},{}".format(mono1, fs))

		self.StyleSetSpec(wx.stc.STC_C_STRINGEOL, "fore:{},{}".format(green, fs))
		self.StyleSetSpec(wx.stc.STC_C_REGEX, "fore:{},{}".format(cyan, fs))
		# Unknown items
		self.StyleSetSpec(wx.stc.STC_C_GLOBALCLASS, "fore:{},{}".format(cyan, fs))
		self.StyleSetSpec(wx.stc.STC_C_UUID, "fore:{},{}".format(purple, fs))
		self.StyleSetSpec(wx.stc.STC_C_VERBATIM, "fore:{},{}".format(mono1, fs))

		self.StyleSetSpec(wx.stc.STC_C_COMMENT, "fore:{},{},italic".format(mono3, fs))
		self.StyleSetSpec(wx.stc.STC_C_COMMENTLINE, "fore:{},{},italic".format(mono3, fs))
		self.StyleSetSpec(wx.stc.STC_C_COMMENTDOC, "fore:{},{},italic".format(mono3, fs))
		self.StyleSetSpec(wx.stc.STC_C_COMMENTDOCKEYWORD, "fore:{},{},bold,italic".format(mono3, fs))
		self.StyleSetSpec(wx.stc.STC_C_COMMENTDOCKEYWORDERROR, "fore:{},{},underline,italic".format(mono3, fs))

		self.SetCaretForeground(wx.Colour(82, 139, 255))
		self.SetCaretWidth(2)
		self.SetCaretLineBackground(wx.Colour(44, 50, 60))
		self.SetCaretLineVisible(True)
		self.SetSelAlpha(20)

		self.SetEdgeMode(wx.stc.STC_EDGE_LINE)
		self.SetEdgeColumn(80)

		self.SetUseTabs(True)
		self.SetTabWidth(self.indent)
		self.SetIndentationGuides(1)

		# Keywords
		self.SetKeyWords(0,
			"and and_eq asm bitand bitor break case catch compl const_cast "
			"continue decltype default delete do dynamic_cast else false for "
			"friend goto if new not not_eq noexcept nullptr operator or or_eq "
			"private protected public reinterpret_cast return sizeof static "
			"static_cast switch this throw true try typeid using while xor xor_eq"
		)
		# Types
		self.SetKeyWords(1,
			"auto bool char char16_t char32_t class const constexpr double enum "
			"explicit export extern float inline int long mutable namespace "
			"register short signed struct template typedef typename union "
			"unsigned va_list virtual void volatile wchar_t"
		)
		# Doc keywords
		self.SetKeyWords(2,
			"TODO FIXME XXX author brief bug callgraph category class code date "
			"def depreciated dir dot dotfile else elseif em endcode enddot "
			"endif endverbatim example exception file if ifnot image include "
			"link mainpage name namespace page par paragraph param pre post "
			"return retval section struct subpage subsection subsubsection test "
			"todo typedef union var verbatim version warning $ @ ~ < > # % HACK"
		)

		self.Bind(wx.stc.EVT_STC_CHARADDED, self.OnCharAdded)

	def UpdateMargins(self):
		line_amount = self.GetText().count("\n")+1
		self.SetMarginWidth(1, 12.5*(math.floor(math.log(line_amount, 10))+1))
	def SetText(self, text):
		wx.stc.StyledTextCtrl.SetText(self, text)
		self.UpdateMargins()
	def OnCharAdded(self, event):
		newline = ord("\r")
		if not self.GetEOLMode() == wx.stc.STC_EOL_CR:
			newline = ord("\n")

		key = event.GetKey()
		if key == newline:
			line = self.GetCurrentLine()
			indent = self.GetLineIndentation(line-1)

			last_line = self.GetLineText(line-1)
			if last_line and last_line[-1] in "{[(":
				indent += self.indent

			self.SetLineIndentation(line, indent)
			self.GotoPos(self.GetCurrentPos()+1)
		elif key == ord("}"):
			line = self.GetCurrentLine()
			if self.GetLine(line).strip() == "}":
				indent = self.GetLineIndentation(line-1)

				indent -= self.indent

				self.SetLineIndentation(line, indent)
				self.GotoPos(self.GetCurrentPos()+indent)

		self.top.setUnsaved()

		self.UpdateMargins()
		self.Colourise(0, -1)
