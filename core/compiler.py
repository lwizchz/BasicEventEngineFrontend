# Copyright (c) 2017-18 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEEF.
# BEEF is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

import os
import errno
import subprocess
import shutil

from resources.enum import ECompile

def copytree(src, dst, symlinks=False):
	names = os.listdir(src)
	if not os.path.isdir(dst):
		os.makedirs(dst)
	errors = []
	for name in names:
		srcname = os.path.join(src, name)
		dstname = os.path.join(dst, name)
		try:
			if symlinks and os.path.islink(srcname):
				linkto = os.readlink(srcname)
				os.symlink(linkto, dstname)
			elif os.path.isdir(srcname):
				copytree(srcname, dstname, symlinks)
			else:
				shutil.copy2(srcname, dstname)
			# XXX What about devices, sockets etc.?
		except OSError as why:
			errors.append((srcname, dstname, str(why)))
	try:
		shutil.copystat(src, dst)
	except OSError as why:
		# can't copy file access times on Windows
		if why.winerror is None:
			errors.extend((src, dst, str(why)))
	if errors:
		raise Error(errors)

class Compiler:
	def __init__(self, top):
		self.top = top
		self.srcDir = "{}/BasicEventEngine".format(self.top.getDir())
		self.resDir = "{}/resources".format(self.srcDir)

	def compile(self, type):
		print("Generating {} resources...".format(self.top.gameCfg["game_name"]))
		self._createDir(self.resDir)
		self._generate()
		self._copyConfigs()
		self._copyExtras()

		if type == ECompile.DEBUG:
			print("Compiling {} in debug mode...".format(self.top.gameCfg["game_name"]))
			self.top.SetStatusText("Compiling game...")
			rc = subprocess.call(["./build.sh", "debug", "build", "echo"], cwd="{}".format(self.srcDir))
			if rc != 0:
				self.top.SetStatusText("Compile failed!")
				return 2
			self.top.SetStatusText("")
		elif type == ECompile.RELEASE:
			print("Compiling {} in release mode...".format(self.top.gameCfg["game_name"]))
			self.top.SetStatusText("Compiling game...")
			rc = subprocess.call(["./build.sh", "release", "build", "echo"], cwd="{}".format(self.srcDir))
			if rc != 0:
				self.top.SetStatusText("Compile failed!")
				return 2
			self.top.SetStatusText("")
		else:
			print("Unknown compile type: {}".format(type))
			return 1

		return 0
	def run(self):
		print("Running {}...".format(self.top.gameCfg["game_name"]))
		self._copyResources()
		subprocess.Popen(["./build/{}".format(self.top.gameCfg["game_name"]), "--no-assert"], cwd="{}".format(self.srcDir))
	def debug(self):
		print("Debugging {}...".format(self.top.gameCfg["game_name"]))
		subprocess.Popen(["gdb", "./build/{}".format(self.top.gameCfg["game_name"])], cwd="{}".format(self.srcDir))
	def clean(self):
		print("Cleaning {}...".format(self.top.gameCfg["game_name"]))
		#subprocess.call(["./build.sh", "clean", "build"], cwd="{}".format(self.srcDir))
		subprocess.call(["git", "clean", "-fd"], cwd=self.srcDir)
		subprocess.call(["git", "reset", "HEAD", "--hard"], cwd=self.srcDir)
	def package(self):
		print("Packaging {}...".format(self.top.gameCfg["game_name"]))
		subprocess.call(["./package.sh"], cwd="{}".format(self.srcDir))

	def _createDir(self, path):
		try:
			os.makedirs(path)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise

	def _generate(self):
		#shutil.rmtree("{}/resources".format(self.srcDir))

		self._generateObjects()
		self._generateRooms()
		self._generateResources()
		self._generateExtras()
		self._generateCMake()
	def _generateObjects(self):
		self._createDir(self.resDir+"/objects")

		headerTemplate = ""
		with open("templates/object.hpp", "r") as headerTemplateFile:
			headerTemplate = headerTemplateFile.read()
		objTemplate = ""
		with open("templates/object.cpp", "r") as objTemplateFile:
			objTemplate = objTemplateFile.read()

		for o in self.top.objects:
			is_persistent = ""
			if o.properties["is_persistent"]:
				is_persistent = "this->set_is_persistent(true);"

			objHeader = headerTemplate.format(
				capname=o.name.upper(),
				objname=o.name.replace("_", " ").title().replace(" ", ""),
				events="\n\t\t".join(o.getEventHeaders())
			)
			obj = objTemplate.format(
				capname=o.name.upper(),
				name=o.name,
				headers=o.getExtraHeaders(),
				objname=o.name.replace("_", " ").title().replace(" ", ""),
				implevents=",\n\t\t".join(o.getImplementedEvents()),
				is_persistent=is_persistent,
				events="\n".join(o.getEvents())
			)
			with open("{}/objects/{}.hpp".format(self.resDir, o.name), "w") as objHeaderFile:
				objHeaderFile.write(objHeader)
			with open("{}/objects/{}.cpp".format(self.resDir, o.name), "w") as objFile:
				objFile.write(obj)
	def _generateRooms(self):
		self._createDir(self.resDir+"/rooms")

		headerTemplate = ""
		with open("templates/room.hpp", "r") as headerTemplateFile:
			headerTemplate = headerTemplateFile.read()
		roomTemplate = ""
		with open("templates/room.cpp", "r") as roomTemplateFile:
			roomTemplate = roomTemplateFile.read()

		for r in self.top.rooms:
			roomHeader = headerTemplate.format(
				capname=r.name.upper(),
				roomname=r.name.replace("_", " ").title().replace(" ", ""),
				events="\n\t\t".join(r.getEventHeaders())
			)
			room = roomTemplate.format(
				capname=r.name.upper(),
				name=r.name,
				roomname=r.name.replace("_", " ").title().replace(" ", ""),
				width=r.properties["width"],
				height=r.properties["height"],
				gravity=r.properties["gravity"],
				events="\n".join(r.getEvents())
			)
			with open("{}/rooms/{}.hpp".format(self.resDir, r.name), "w") as roomHeaderFile:
				roomHeaderFile.write(roomHeader)
			with open("{}/rooms/{}.cpp".format(self.resDir, r.name), "w") as roomFile:
				roomFile.write(room)
			with open("{}/rooms/{}.csv".format(self.resDir, r.name), "w") as instanceFile:
				instanceFile.write("\n".join(r.getInstanceMap()))

		mainTemplate = ""
		with open("templates/main.cpp", "r")  as mainTemplateFile:
			mainTemplate = mainTemplateFile.read()
		firstRoom = self.top.gameCfg["first_room"]
		if not firstRoom:
			firstRoom = self.top.rooms[0].name
		main = mainTemplate.format(
			firstRoom=firstRoom
		)
		with open("{}/main.cpp".format(self.srcDir), "w") as mainFile:
			mainFile.write(main)
	def _generateResources(self):
		resourcesHeader = ""
		with open("templates/resources.hpp", "r") as resourcesHeaderTemplate:
			resourcesHeader = resourcesHeaderTemplate.read()
		resourcesHeader = resourcesHeader.format(
			textureDefines="\n".join(["extern bee::Texture* {};".format(s.name) for s in self.top.textures]),
			soundDefines="\n".join(["extern bee::Sound* {};".format(s.name) for s in self.top.sounds]),
			fontDefines="\n".join(["extern bee::Font* {};".format(f.name) for f in self.top.fonts]),
			pathDefines="\n".join(["extern bee::Path* {};".format(p.name) for p in self.top.paths]),
			timelineDefines="\n".join(["extern bee::Timeline* {};".format(t.name) for t in self.top.timelines]),
			meshDefines="\n".join(["extern bee::Mesh* {};".format(m.name) for m in self.top.meshes]),
			lightDefines="\n".join(["extern bee::Light* {};".format(l.name) for l in self.top.lights]),
			objectDefines="\n".join(["extern bee::Object* {};".format(o.name) for o in self.top.objects]),
			roomDefines="\n".join(["extern bee::Room* {};".format(r.name) for r in self.top.rooms])
		)
		with open(self.resDir+"/resources.hpp", "w") as resourcesHeaderFile:
			resourcesHeaderFile.write(resourcesHeader)

		resources = ""
		with open("templates/resources.cpp", "r") as resourcesTemplate:
			resources = resourcesTemplate.read()
		resources = resources.format(
			textureDefines="\n".join(["bee::Texture* {} = nullptr;".format(s.name) for s in self.top.textures]),
			soundDefines="\n".join(["bee::Sound* {} = nullptr;".format(s.name) for s in self.top.sounds]),
			fontDefines="\n".join(["bee::Font* {} = nullptr;".format(f.name) for f in self.top.fonts]),
			pathDefines="\n".join(["bee::Path* {} = nullptr;".format(p.name) for p in self.top.paths]),
			timelineDefines="\n".join(["bee::Timeline* {} = nullptr;".format(t.name) for t in self.top.timelines]),
			meshDefines="\n".join(["bee::Mesh* {} = nullptr;".format(m.name) for m in self.top.meshes]),
			lightDefines="\n".join(["bee::Light* {} = nullptr;".format(l.name) for l in self.top.lights]),
			objectDefines="\n".join(["bee::Object* {} = nullptr;".format(o.name) for o in self.top.objects]),
			roomDefines="\n".join(["bee::Room* {} = nullptr;".format(r.name) for r in self.top.rooms]),

			objectIncludes="\n".join(["#include \"objects/{}.hpp\"".format(o.name) for o in self.top.objects]),
			roomIncludes="\n".join(["#include \"rooms/{}.hpp\"".format(r.name) for r in self.top.rooms]),

			textureInits="\n\t\t".join(["{name} = new Texture(\"{name}\", \"{path}\");{extra}".format(name=s.name, path=s.name+".png", extra=s.getInit()) for s in self.top.textures]),
			soundInits="\n\t\t".join(["{name} = new Sound(\"{name}\", \"{path}\", false);{extra}".format(name=s.name, path=s.name+".wav", extra=s.getInit()) for s in self.top.sounds]),
			fontInits="\n\t\t".join(["{name} = new Font(\"{name}\", \"{path}\", {size}, false);{extra}".format(name=f.name, path=f.name+".ttf", size=f.properties["size"], extra=f.getInit()) for f in self.top.fonts]),
			pathInits="\n\t\t".join(["{name} = new Path(\"{name}\", \"\");{extra}".format(name=p.name, extra=p.getInit()) for p in self.top.paths]),
			timelineInits="\n\t\t".join(["{name} = new Timeline(\"{name}\", \"\");{extra}".format(name=t.name, extra=t.getInit()) for t in self.top.timelines]),
			meshInits="\n\t\t".join(["{name} = new Mesh(\"{name}\", \"{path}\");{extra}".format(name=m.name, path=m.name+".obj", extra=m.getInit()) for m in self.top.meshes]),
			lightInits="\n\t\t".join(["{name} = new Light(\"{name}\", \"\");{extra}".format(name=l.name, extra=l.getInit()) for l in self.top.lights]),
			objectInits="\n\t\t".join(["{name} = new {objname}();{extra}".format(name=o.name, objname=o.name.replace("_", " ").title().replace(" ", ""), extra=o.getInit()) for o in self.top.objects]),
			roomInits="\n\t\t".join(["{name} = new {roomname}();{extra}".format(name=r.name, roomname=r.name.replace("_", " ").title().replace(" ", ""), extra=r.getInit()) for r in self.top.rooms]),

			textureDeletes="\n\t".join(["DEL({});".format(s.name) for s in self.top.textures]),
			soundDeletes="\n\t".join(["DEL({});".format(s.name) for s in self.top.sounds]),
			fontDeletes="\n\t".join(["DEL({});".format(f.name) for f in self.top.fonts]),
			pathDeletes="\n\t".join(["DEL({});".format(p.name) for p in self.top.paths]),
			timelineDeletes="\n\t".join(["DEL({});".format(t.name) for t in self.top.timelines]),
			meshDeletes="\n\t".join(["DEL({});".format(m.name) for m in self.top.meshes]),
			lightDeletes="\n\t".join(["DEL({});".format(l.name) for l in self.top.lights]),
			objectDeletes="\n\t".join(["DEL({});".format(o.name) for o in self.top.objects]),
			roomDeletes="\n\t".join(["DEL({});".format(r.name) for r in self.top.rooms])
		)
		with open(self.resDir+"/resources.cpp", "w") as resourcesFile:
			resourcesFile.write(resources)
	def _generateExtras(self):
		extras = ""
		with open("templates/extras.hpp") as extrasTemplate:
			extras = extrasTemplate.read()
		extras = extras.format(
			extras="\n".join(["#include \"extras/{}\"".format(extra.name) for extra in self.top.extras if os.path.splitext(extra.name)[1] == ".hpp"])
		)
		with open(self.resDir+"/extras.hpp", "w") as extrasFile:
			extrasFile.write(extras)
	def _generateCMake(self):
		config = ""
		with open("templates/config.sh", "r") as configTemplate:
			config = configTemplate.read()
		config = config.format(
			game=self.top.gameCfg["game_name"],
			v_major=self.top.gameCfg["game_version_major"],
			v_minor=self.top.gameCfg["game_version_minor"],
			v_release=self.top.gameCfg["game_version_release"]
		)
		with open(self.srcDir+"/config.sh", "w") as configFile:
			configFile.write(config)

		cmake = ""
		with open("templates/resources.CMakeLists.txt", "r") as cmakeTemplate:
			cmake = cmakeTemplate.read()
		cmake = cmake.format(
			objects=" ".join(["objects/{}.cpp".format(obj.name) for obj in self.top.objects]),
			rooms=" ".join(["rooms/{}.cpp".format(room.name) for room in self.top.rooms]),
			extras=" ".join(["extras/{}".format(extra.name) for extra in self.top.extras if os.path.splitext(extra.name)[1] == ".cpp"])
		)
		with open(self.resDir+"/CMakeLists.txt", "w") as cmakeFile:
			cmakeFile.write(cmake)

		shutil.copyfile("templates/CMakeLists.txt", "{}/CMakeLists.txt".format(self.srcDir))

	def _copyConfigs(self):
		if self.top.configs:
			shutil.rmtree("{}/cfg".format(self.srcDir))
			copytree("{}/cfg".format(self.top.rootDir), "{}/cfg".format(self.srcDir))
	def _copyExtras(self):
		copytree("{}/resources/extras".format(self.top.rootDir), "{}/resources/extras".format(self.srcDir))
	def _copyResources(self):
		copytree("{}/resources".format(self.top.rootDir), "{}/resources".format(self.srcDir))
