import os,sys

sys.path.append("/opt/livingdata/lib")
from livdatscenario import *

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



class RigvedaGen(ScenarioGenerator):
	def __init__(self,*args, **kwargs):
		super(RigvedaGen,self).__init__(*args, **kwargs)
		self.cardsheet=self.scenariobook.worksheet_by_title("Cards")
		self.testrigsheet=self.scenariobook.worksheet_by_title("Cards")
		self.cardsdf=self.cardsheet.get_as_df()
		self.testrigdf=self.testrigsheet.get_as_df()
	
	def update_testrigsheet(rigvals):
		rownum=2
		tsval=self.testrigsheet.get_row(rownum)
		if tsval==['']:
			self.testrigsheet.update_row(2,rigvals)
		else:
			while tsval != ['']:
				rownum+=1
				tsval=self.testrigsheet.get_row(rownum)
			self.testrigsheet.update_row(rownum,rigvals)

	def get_testrig_latest(self):
		rownum=2
		tsval=self.testrigsheet.get_row(rownum)
		if tsval==['']:
			return None
		else:
			while tsval != ['']:
				rownum+=1
				tsval=self.testrigsheet.get_row(rownum)
			return self.testrigsheet.get_row(rownum-1)

	def get_attribs_for_card(self,cardname,expected=True):
		cardattribs={"cardname":cardname}
		carddict=self.cardsdf.loc[self.cardsdf['cardname']==cardname].transpose().to_dict().values()[0]
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
			

		
		
