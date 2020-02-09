from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

#page for pkidb
page = 'http://www.icoa.fr/pkidb/'


#making a file name
filename = "pkidb.csv"
f = open(filename, "w")

#adding header
headers = "Inhibitor,Target,MW,Smiles, InChiKey,Synonyms,Images,ID\n"  #adding header to file
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

#finding each inhibitor by row (tr)
all_tr = table.findAll("tr")
  

f = open(filename, "a+") #open file to append

for each in all_tr:
	try:
		#extracting the name of the inhibitor
		inhibitor = each.td.b
		inhibitor = inhibitor.text

		#each row has value in columns made up by td
		TD = each.findAll("td")

		#extracting the target
		Target1 = str(TD[16]).replace("<br/>", ",")
		Target2 = Target1.strip("<td></")

		#extracting the molecular weight
		MW = TD[9].text

		#extracting smiles formula
		smiles = each.find("td", {"style":"word-wrap: break-word; max-width: 250px;"})
		s = smiles.text        #smiles and inchikey are found together in one text
		start = 'Smiles=;'     #extracting text after "Smiles="
		end = 'InChiKey'       # and before "InChiKey"
		SMILES= s[s.find(start)+len(start):s.rfind(end)]

		#extracting InchiKey
		KEY = s.split('InChiKey=')[-1]

		#extracting synonyms
		synonyms= TD[-3].get_text(strip=True, separator=',')

		#extracting image link 
		image = each.td
		image1 = str(image.img["src"])  #src only gives the end of the link e.g 'static/img/mol/Leniolisib.svg'
		URL= "http://www.icoa.fr/pkidb/" #this is the start of the link

		IMAGE = URL + image1   #together we get 

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
			else:
			    pass
			if must_have in ChemblID_link1:
			    ID = ChemblID_link1.split('inspect/')[-1]
			    return ID
			else:
			    pass
			if must_have in ChemblID_link2:
			    ID = ChemblID_link2.split('inspect/')[-1]
			    return ID  
			else:
			    pass

		ID = chemblID(each)
		#adding the results to the file
		f.write('"{}","{}","{}","{}","{}","{}", "{}", "{}"'.format(inhibitor, Target2, MW, SMILES, KEY, synonyms, IMAGE, ID )+ "\n")
	
	except:
		continue

f.close()


