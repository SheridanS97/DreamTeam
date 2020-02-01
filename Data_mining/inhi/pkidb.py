from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

#page for pkidb
page = 'http://www.icoa.fr/pkidb/'


#making a file name
filename = "pkidb.csv"
f = open(filename, "w")
headers = "Inhibitor,Target,MW,Smiles,Synonyms,Images, ID\n"  #adding header to file
f.write(headers)
f.close()


#opening connection, grabbing page
uClient = uReq(page)
page_html = uClient.read()
uClient.close


#html parse
page_soup = soup(page_html, 'html.parser')

#grabbing content of just the body of the table
table = page_soup.table.tbody

#each inhibitor information separated by tr
all_tr = table.findAll("tr")
  

f = open(filename, "a+") #open file to append

for each in all_tr:
	try:
		#extracts the name of the inhibitor
		inhibitor = each.td.b
		inhibitor = inhibitor.text

		TD = each.findAll("td")
		Target1 = str(TD[16]).replace("<br/>", ",")
		Target2 = Target1.strip("<td></")

		MW = TD[9].text

		smiles = each.find("td", {"style":"word-wrap: break-word; max-width: 250px;"})
		smiles1 = smiles.text

		synonyms= str(TD[-3].text).replace("  ", ",")

		image = each.td
		image1 = str(image.img["src"])
		URL= "http://www.icoa.fr/pkidb/"

		IMAGE = URL + image1

		def chemblID(each):
		    ChemblID0 = each.findAll("td")[4].findAll("a")[0]
		    ChemblID1 = each.findAll("td")[4].findAll("a")[1]
		    ChemblID2 = each.findAll("td")[4].findAll("a")[2]
		    
		    ChemblID_link0 = ChemblID0.get("href")
		    ChemblID_link1 = ChemblID1.get("href")
		    ChemblID_link2 = ChemblID2.get("href")
		    
		    must_have = "CHEMBL"

		    if must_have in ChemblID_link0:
		        ID = ChemblID_link0.split('inspect/')[-1]
		        return ID
		    if must_have in ChemblID_link1:
		        ID = ChemblID_link1.split('inspect/')[-1]
		        return ID
		    if must_have in ChemblID_link2:
		        ID = ChemblID_link2.split('inspect/')[-1]
		        return ID 

		ID = chemblID(each)
		#adding the results to the file
		f.write('"{}","{}","{}","{}","{}","{}", "{}"'.format(inhibitor, Target2, MW, smiles1, synonyms, IMAGE, ID )+ "\n")
	
	except:
		pass

f.close()


