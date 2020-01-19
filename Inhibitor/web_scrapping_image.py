from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

#6 pages of inhibitor information
page0 = 'http://www.kinase-screen.mrc.ac.uk/kinase-inhibitors'
page1 = 'http://www.kinase-screen.mrc.ac.uk/kinase-inhibitors?page=1'
page2 = 'http://www.kinase-screen.mrc.ac.uk/kinase-inhibitors?page=2'
page3 = 'http://www.kinase-screen.mrc.ac.uk/kinase-inhibitors?page=3'
page4 = 'http://www.kinase-screen.mrc.ac.uk/kinase-inhibitors?page=4'
page5 = 'http://www.kinase-screen.mrc.ac.uk/kinase-inhibitors?page=5'


#making a file name
filename = "inhibitors_images.csv"
f = open(filename, "w")
headers = "Inhibitor,Images\n"  #adding header to file
f.write(headers)
f.close()


def each_page(url_):
	#opening connection, grabbing page
	uClient = uReq(url_)
	page_html = uClient.read()
	uClient.close

	#html parse
	page_soup = soup(page_html, 'html.parser')

	#total 50 inhibitor in one page, 25 under odd, 25 under class even. 
	#except last page. has 5 inhibitors.
	even = page_soup.findAll("tr", {"class": "even" })  #25
	odd = page_soup.findAll("tr", {"class": "odd"})    #25

	f = open(filename, "a+") #open file to append

	for each in odd:
		try:
			#extracts the name of the inhibitor
			inhibitor = each.td.a.text

			#extracts the link of the image
			image_link = each.findAll("td", {"class": "views-field views-field-field-structure-image"})
			final_image = image_link[0].a["href"]

			#adding the results to the file
			f.write((inhibitor) + "," + final_image + "\n")

		except:     #if no image/error then empty space
			final_image = ""
			f.write((inhibitor) + "," + final_image + "\n")

		
	for every in even:
		try:
			#extracts the name of the inhibitor
			inhibitor = every.td.a.text

			#extracts the link of the image
			image_link = every.findAll("td", {"class": "views-field views-field-field-structure-image"})
			final_image = image_link[0].a["href"]
			
			#adding the results to the file
			f.write((inhibitor) + "," + final_image + "\n")

		except:        #if there is no image link then empty space
			final_image = ""
			f.write((inhibitor) + "," + final_image + "\n")

		

	f.close()

each_page(page0)
each_page(page1)
each_page(page2)
each_page(page3)
each_page(page4)
each_page(page5)