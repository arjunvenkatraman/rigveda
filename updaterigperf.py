#!/usr/bin/python
import os,sys
sys.path.append("/opt/rigveda/lib")
from rigveda import *
import ConfigParser




if __name__=="__main__":
	configfile=sys.argv[1]
	rigvedagen=RigvedaGen(configfile,launchbrowser=False,headless=True)
	rigvedagen.update_testrigsheet()
