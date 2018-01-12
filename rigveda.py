import os,sys

sys.path.append("/opt/livingdata/lib")
sys.path.append("/opt/SoMA/python/lib")
from livdattable import *
from libsoma import *
import pygsheets
from bs4 import BeautifulSoup
	
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
    page=urllib2.urlopen(url).read()
    bs=BeautifulSoup(page,"html")
    panels=bs.find("div",{"class":"col-lg-3"}).find_all("div",{"class":"panel"})
    for panel in panels:
        listitems=panel.find_all("li",{"class":"list-group-item"})
        for listitem in listitems:
            line=listitem.text.strip().split("\n")
            if "Earning in last 24 hours" in line:
                earning=line[0].split(" ETH")[0]
            if "Current approx.speed" in line:
				curhashrate=float(line[0].replace(" mhs",""))
            print line
        ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	
    return [ts,curhashrate,earning]

	
def setup_rigveda_sheet(skey,outhfile,outhstore):
	sheet={}
	gc=pygsheets.authorize(outh_file=outhfile,outh_nonlocal=True,outh_creds_store=outhstore)
	rigvedasheet=gc.open_by_key(skey)
	sheet['rigvedasheet']=rigvedasheet
	sheet['cardsheet']=rigvedasheet.worksheet_by_title("Cards")
	sheet['calcsheet']=rigvedasheet.worksheet_by_title("CalcSheet")
	sheet['testrigsheet']=rigvedasheet.worksheet_by_title("TestRig")
	sheet['calckey']=rigvedasheet.worksheet_by_title("CalcKey")
	return sheet


def get_testrig_latest(testrigsheet):
	rownum=2
	tsval=testrigsheet.get_row(rownum)
	if tsval==['']:
		return None
	else:
		while tsval != ['']:
			rownum+=1
			tsval=testrigsheet.get_row(rownum)
		return testrigsheet.get_row(rownum-1)

def get_cell_for_value(sheetkey,valuename):
    return sheetkey.loc[sheetkey['Value']==valuename,"Cell"].iloc[0]

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
    
def get_calckeyvars(sheet,sheetkey):
    calckeyvars=sheetkey.Value.to_dict().values()
    return calckeyvars

def get_cur_scenario(sheet):
    scenario={}
    sheetkey=sheet['calckey'].get_as_df()
    calckeyvars=get_calckeyvars(sheet,sheetkey)
    for var in calckeyvars:
        print var,get_cell_for_value(sheetkey,var),sheet['calcsheet'].cell(str(get_cell_for_value(sheetkey,var))).value
        scenario[var]=sheet['calcsheet'].cell(str(get_cell_for_value(sheetkey,var))).value
    return scenario
    
    
