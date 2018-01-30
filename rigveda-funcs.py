import os,sys

sys.path.append("/opt/livingdata/lib")
sys.path.append("/opt/SoMA/python/lib")
from livdattable import *
from libsoma import *
import pygsheets
from bs4 import BeautifulSoup

#Update functions

def update_testrigsheet(testrigsheet,rigvals):
	rownum=2
	tsval=testrigsheet.get_row(rownum)
	if tsval==['']:
		testrigsheet.update_row(2,rigvals)
	else:
		while tsval != ['']:
			rownum+=1
			tsval=testrigsheet.get_row(rownum)
		testrigsheet.update_row(rownum,rigvals)


def get_last_24hr_earn_dwarfpool(url):
    print "opening url "+ url + "..."
    page=urllib2.urlopen(url).read()
    bs=BeautifulSoup(page,"lxml")
    panels=bs.find("div",{"class":"col-lg-3"}).find_all("div",{"class":"panel"})
    for panel in panels:
        listitems=panel.find_all("li",{"class":"list-group-item"})
        for listitem in listitems:
            line=listitem.text.strip().split("\n")
            if "Earning in last 24 hours" in line:
                earning=line[0].split(" ETH")[0]
            if "Current approx.speed" in line:
				curhashrate=float(line[0].replace(" mhs",""))
        ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	
    return [ts,curhashrate,earning]



#Setup functions

def setup_config(configfile):
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
		try:
			rigvals=get_last_24hr_earn_dwarfpool(statusurl)
		except:
			rigvals=[]
			print "Dwarves did not respond"
	print "Setting up th rigveda sheet..."
	sheet=setup_rigveda_sheet(rigsheetkey,outhfile,outhstore)
	if rigvals!=[]:
		print "Updating the testrigsheet"
		update_testrigsheet(sheet['testrigsheet'],rigvals)
	return sheet

def get_calckey(sheet):
    sheetkey=sheet['calckey'].get_as_df()
    return sheetkey

def setup_rigveda_sheet(skey,outhfile,outhstore):
	sheet={}
	gc=pygsheets.authorize(outh_file=outhfile,outh_nonlocal=True,outh_creds_store=outhstore)
	rigvedasheet=gc.open_by_key(skey)
	sheet['rigvedasheet']=rigvedasheet
	
	
'''
	sheet['rigvedasheet']=rigvedasheet
	sheet['cardsheet']=rigvedasheet.worksheet_by_title("Cards").get_as_df()
	sheet['calcsheet']=rigvedasheet.worksheet_by_title("CalcSheet").get_as_df()
	sheet['testrigsheet']=rigvedasheet.worksheet_by_title("TestRig").get_as_df()
	sheet['calckey']=rigvedasheet.worksheet_by_title("CalcKey").get_as_df()
	sheet['scenarios']=rigvedasheet.worksheet_by_title("Scenarios").get_as_df()
	sheet['calckeydf']=sheet['calckey'].get_as_df()
	return sheet
'''

#Read/Write Functions
def get_sheet_latest_row(sheet):
	rownum=2
	rowval=sheet.get_row(rownum)
	if rowval==['']:
		return None
	else:
		while rowval != ['']:
			rownum+=1
			rowval=sheet.get_row(rownum)
		return sheet.get_row(rownum-1)

def get_cell_for_value(calckey,valuename):
    return str(calckey.loc[calckey.Value==valuename].Cell.iloc[0])

def load_scenario_cardvals(scenario,cardvals):
	for key in cardvals.keys():
		scenario[key]=cardvals[key]
	return scenario

	
def get_result_value(valuename,sheet,calckey):
	print "Trying to get value for "+ valuename
	cell=get_cell_for_value(calckey,valuename)
	value=sheet['calcsheet'].cell(cell).value
	return value


def set_variable_value(valuename,value,sheet,calckey):
	print "Trying to set value for "+ valuename
	cell=get_cell_for_value(calckey,valuename)
	try:
		sheet['calcsheet'].update_cell(cell,value)
	except:
		print "Could not update"


def update_scenario_curvals(scenario,sheet,calckey):
	scenariocols=sheet['scenarios'].get_row(1)
	for columnname in scenariocols:
		try:
			curval=get_curvalue(columnname,sheet,calckey)
		except:
			if columnname not in scenario.keys():
				curval=""
			else:
				curval=scenario[columnname]
		scenario[columnname]=curval
	return scenario



def get_attribs_for_card(cardsdf,cardname,expected=True):
	cardattribs={"cardname":cardname}
	
	carddict=cardsdf.loc[cardsdf['cardname']==cardname].transpose().to_dict().values()[0]
	if carddict['observedhashrate'] !="":
		cardattribs['cardmhs']=carddict['observedhashrate']
		cardattribs['cardpower']=carddict['obspowerdrawwatts']
	else:
		if expected==True:
			cardattribs['cardmhs']=carddict['expectedhashrate']
			cardattribs['cardpower']=carddict['exppowerdrawwatts']
		else:
			cardattribs['cardmhs']=carddict['claimedhashrate']
			cardattribs['cardpower']=carddict['claimedpowerdrawwatts']
	if carddict['priceusd']!="":
		cardattribs['cardprice']=carddict['priceusd']
	else:
		cardattribs['cardprice']=None
	
	return cardattribs

    
def get_sheetcalckey(sheet):
    sheetkey=sheet['calckey'].get_as_df()
    return sheetkey


def get_cur_scenario(sheet):
    scenario={}
    sheetkey=sheet['calckey'].get_as_df()
    calckeyvars=get_calckeyvars(sheet,sheetkey)
    for var in calckeyvars:
        print var,get_cell_for_value(sheetkey,var),sheet['calcsheet'].cell(str(get_cell_for_value(sheetkey,var))).value
        scenario[var]=sheet['calcsheet'].cell(str(get_cell_for_value(sheetkey,var))).value
    return scenario
    

def set_scenario_card(scenario,cardname,cardsdf):
	#cardsdf=sheet['cardsheet'].get_as_df()
	cardvals=get_attribs_for_card(cardsdf,cardname)
	scenario=load_scenario_cardvals(scenario,cardvals)
	return scenario
	

def get_scenario_vars(scenario,calckey):
	varnames=[]
	for colname in scenario.keys():
		if colname in calckey.Value.to_dict().values():
			if calckey.loc[calckey.Value==colname].Type.iloc[0]=="variable":
				varnames.append(colname)
	return varnames


def get_scenario_results(scenario,calckey):
	resnames=[]
	for colname in scenario.keys():
		if colname in calckey.Value.to_dict().values():
			if calckey.loc[calckey.Value==colname].Type.iloc[0]=="result":
				resnames.append(colname)
	return resnames
	

def load_scenario_variables(scenario,sheet,calckey):
	varnames=get_scenario_vars(scenario,calckey)
	for var in varnames:
		print var,scenario[var]
		set_curvalue(var,scenario[var],sheet,calckey)


def show_scenario(scenario):
	print get_color_json(scenario)
	

def get_new_scenario(sheet,calckey,blank=False):
	scenario={}
	scenariocols=sheet['scenarios'].get_row(1)
	print scenariocols
	for columnname in scenariocols:
		try:
			curval=get_curvalue(columnname,sheet,calckey)
		except:
			if columnname not in scenario.keys():
				curval=""
			else:
				curval=scenario[columnname]
		if blank==True:
			curval=""
		scenario[columnname]=curval
	return scenario


def set_ranges(scenario,calckey):
	varnames=get_scenario_vars(scenario,calckey)
	ranges={}
	for var in varnames:
		ranges[var]=range(0,1)
	return ranges
	

def zero_results(scenario,calckey):
	resnames=get_scenario_results(scenario,calckey)
	for res in resnames:
		scenario[res]=""
	return scenario


def update_scenarios(sheet,newscenarios):
	scenarios=sheet['scenarios'].get_as_df()
	print len(scenarios)
	scenarios=scenarios.append(newscenarios,ignore_index=True)
	print len(scenarios)
	sheet['scenarios'].set_dataframe(scenarios,(1,1))
