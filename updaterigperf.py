#!/usr/bin/python
from rigveda import *
import ConfigParser




if __name__=="__main__":
	configfile=sys.argv[1]
	config=ConfigParser.ConfigParser()
	config.read(configfile)

	outhstore = config.get("Google","outhstore")
	outhfile = config.get("Google","outhfile")
	rigsheetkey=config.get("Rig","rigsheetkey")
	rigname=config.get("Rig","rigname")
	statusurl=config.get("Pool","statusurl")
	poolname=config.get("Pool","poolname")
	print "Read config for " + rigname
	if poolname=="DwarfPool":
		print "getting status from the dwarves...."
		rigvals=get_last_24hr_earn_dwarfpool(statusurl)
	print "Setting up th rigveda sheet..."
	sheet=setup_rigveda_sheet(rigsheetkey,outhfile,outhstore)
	print "Updating the testrigsheet"
	update_testrigsheet(sheet['testrigsheet'],rigvals)
