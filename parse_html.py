from bs4 import BeautifulSoup
import json
import re

def extract_contacts(OBJ , children):
    ## LOOP FIRST TO EXTRACT PHONE EMAIL etc, excet for address
    children = children.split('\n')
    count = 1
    address = []
    for child in children[1:]:
        temp = child.lower()
        child = child.replace('\n','')
        child = child.replace('\t','')
        if 'fax' in temp:
            OBJ["phone"] = OBJ.get("phone" , {})
            OBJ["phone"]["fax"] = re.sub(' +', ' ', child.split()[1])
        elif 'phone' in temp:
            OBJ["phone"] = OBJ.get("phone" , {})
            OBJ["phone"]["main"] = re.sub(' +', ' ', child.split()[1])
            #Extract City 
            cityIndex = children.index(child) - 1
            details = children[cityIndex].split(',')
        
            OBJ["city"] = re.sub(' +', ' ', details[0].strip())
        
            OBJ["statecode"] = re.sub(' +', ' ', details[1].split()[0].strip())
        
            OBJ["zipcode"] = re.sub(' +', ' ', details[1].split()[1].strip())
        
        elif '@' in temp:
            OBJ["email"] = {}
            OBJ["email"]["main"] = child.strip()
        else:
            #save addresses
            address.append(child.strip())
    #push addresses
    for addr in address[:-2]:
        OBJ["address"+str(count)] = re.sub(' +', ' ', addr)
        count += 1


def extract_links(OBJ , children):
    for child in children:
        text = child.text.strip().lower()
        text = text.replace('\n','')
        text = text.replace('\t','')
        text = text.replace('\u00ae','')
        text = re.sub(' +', ' ', text)
        if text:
            OBJ['links'] = OBJ.get("links",{})
            OBJ["links"][text] = child['href']

def extract_socials(OBJ , children):
    for c in children:
        tag = c.findChildren('a')
        if tag:
            link = tag[0]['href']
            name = tag[0].findChildren('i')[0]['class'][1][3:]
            OBJ["socials"] = OBJ.get("socials" ,{})
            OBJ["socials"][name] = link

            
JSON = []
soup = BeautifulSoup(open("./table.html"), "html.parser")
table = soup.findChildren('table')[0]
rows = table.findChildren(['tr'])
for row in rows[1:]:
    OBJ = {}
    cells = row.findChildren(['td'])
    OBJ["state"] = cells[0].string
    OBJ["state"] = OBJ["state"].replace('\n','')
    OBJ["state"] = OBJ["state"].replace('\t','')
    OBJ["state"] = OBJ["state"] = re.sub(' +', ' ', OBJ["state"])
    contact = cells[1]
    links = cells[2]

    ##Parse the Contacts Cell
    children = contact.findChildren()
    name = children[0].string
    name.replace('\n' , '')
    name.replace('\t' , '')
    OBJ["name"] = re.sub(' +', ' ', name)
    contact.a.decompose()
    children = contact.text
    extract_contacts(OBJ , children[1:])

    ##Parse the Links
    children = links.findChildren('a')
    extract_links(OBJ , children)
    JSON.append(OBJ)

    ##Parse socials
    children = links.findChildren('li')
    if children:
        extract_socials(OBJ , children)
    # print(children)


SORTED = json.dumps(JSON, indent=4, sort_keys=True)
UNSORTED = json.dumps(JSON, indent=4)

with open("data(sorted).json", "w") as outfile: 
    outfile.write(SORTED) 
with open("data(unsorted).json", "w") as outfile: 
    outfile.write(UNSORTED) 
