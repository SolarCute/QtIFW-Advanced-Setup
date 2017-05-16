#!/usr/bin/env python3

import sys
import os
import shutil
import subprocess
from distutils.dir_util import copy_tree
from enum import Enum

# constants
srcdir = sys.argv[1]
outdir = sys.argv[2]
qtifwdir = sys.argv[3]
target = sys.argv[4]
mode = sys.argv[5]
cfgdir = os.path.join(outdir, "config")
pkgdir = os.path.join(outdir, "packages")

# definitions
class State(Enum):
	Config = 0
	Package = 1,
	Meta = 2,
	Data = 3

def copy_cfg(src):
	cfgsrc = os.path.join(srcdir, src)
	cfgout = os.path.join(cfgdir, os.path.basename(src))
	shutil.copy2(cfgsrc, cfgout)

def copy_pkg(pkg, state, src):
	pkgsrc = os.path.join(srcdir, src)
	pkgout = os.path.join(pkgdir, pkg, state.name.lower())
	os.makedirs(pkgout, exist_ok=True)
	copy_tree(pkgsrc, pkgout, preserve_symlinks=True)

def create_install_dir(offset):
	state = State.Config
	pkg = ""
	for arg in sys.argv[offset:]:
		if arg == "p":
			state = State.Package
		elif arg == "m":
			state = State.Meta
		elif arg == "d":
			state = State.Data
		else:
			if state == State.Config:
				copy_cfg(arg)
			elif state == State.Package:
				pkg = arg
			else:
				copy_pkg(pkg, state, arg)
				state = State.Package

def create_offline():
	subprocess.run([
		os.path.join(qtifwdir, "binarycreator"),
		"-f",
		"-c",
		os.path.join(cfgdir, "config.xml"),
		"-p",
		pkgdir,
		os.path.join(outdir, target)
	])

def create_online():
	subprocess.run([
		os.path.join(qtifwdir, "binarycreator"),
		"-n",
		"-c",
		os.path.join(cfgdir, "config.xml"),
		"-p",
		pkgdir,
		os.path.join(outdir, target)
	])

def create_repo():
	subprocess.run([
		os.path.join(qtifwdir, "repogen"),
		"-p",
		pkgdir,
		os.path.join(outdir, "repository")
	])

# prepare & copy files
shutil.rmtree(outdir, ignore_errors=True)
os.makedirs(cfgdir, exist_ok=True)
create_install_dir(6)

# generate installer
if mode == "offline":
	create_offline()
elif mode == "online":
	create_online()
elif mode == "repository":
	create_repo()
elif mode == "online_all":
	create_repo()
	create_online()
else:
	raise "Invalid mode specified: " + mode