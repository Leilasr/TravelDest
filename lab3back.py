# Name:Leila Sarkamari
# Lab 3-CIS 41B 
import urllib.request as ur
import requests
from bs4 import BeautifulSoup 
import re
import json
from json import scanner
import sqlite3
'''
this program read data from site,produce a JSON file and an sqlite database file

'''
def ScrapeData(Datacontainer,siteurl):
    '''
    this function read thehe data are from the website:  https://www.timeout.com/things-to-do/best-places-to-travel
    scrap the data, find "month_name","ranking_number""destination_name","description_text","destination_url"
    and store data in array of dictionary

    '''
    try:
        if not siteurl:
            raise ValueError("The URL is empty.")
        
        page = requests.get(siteurl)
        soup = BeautifulSoup(page.content, "lxml") 
        soup.text.encode('utf8', 'ignore').decode()
        root_url='/'.join(siteurl.split('/')[:3])   #"https://www.timeout.com"
        #print(root_url)
        # _zoneItems_8z2or_5 zoneItems  tile _article_142mc_1  _articleContent_142mc_27  _titleLinkContainer_142mc_45 ,  div article div a
        # _zoneItems_8z2or_5 zoneItems  tile _article_142mc_1  _articleContent_142mc_27  _h3_cuogz_1  ,  div article div h3
        
        month_links=[]
        m_links =soup.select('div._zoneItems_8z2or_5.zoneItems article.tile._article_142mc_1 div._articleContent_142mc_27 a._titleLinkContainer_142mc_45')
        #print(m_links)
        
        for lTag in m_links:
            #print(lTag.text)
            month_links.append((lTag.text,lTag['href'])) 
        #print(month_links)
        for month_link in month_links:
            #print(root_url+month_link[1])
            
        
            # Prepend the root URL to the month link
            month_url = root_url+month_link[1]
            month_response = requests.get(month_url)
            #_zoneItems_882m9_1 zoneItems   tile _article_kc5qn_1   articleContent _articleContent_kc5qn_216   _title_kc5qn_9  _h3_cuogz_1 ,div article div div h3 (span)
            
            month_soup = BeautifulSoup(month_response.content, "lxml")
            travels = month_soup.select('article.tile._article_kc5qn_1 div.articleContent._articleContent_kc5qn_216') 
            #print(len(travels))
            
            for step in travels:
                
                # Extract ranking number, step name, and description text
                ranking_city = step.select_one('div.articleContent._articleContent_kc5qn_216 div._title_kc5qn_9')
                if ranking_city:
                    try:
                        ulr_destination=ranking_city.find('a')['href']
                        if ulr_destination:
                            #ulr_destination=root_url+ulr_destination
                            if not ulr_destination.startswith("http"):
                                ulr_destination=root_url+ulr_destination
                            else:
                                if  ulr_destination.startswith("https"):
                                    ulr_destination = "https://" + ulr_destination.split("://", 1)[-1]
                                if  ulr_destination.startswith("http"):
                                    ulr_destination = "http://" + ulr_destination.split("://", 1)[-1]
                                
                                
                                

                        #print(ulr_destination)                
                    except TypeError:
                        ulr_destination="None"
                        pass            
                       
                    ranking_number=ranking_city.get_text()
                    
                    
                step_name = step.select_one('div.articleContent._articleContent_kc5qn_216 div._title_kc5qn_9 h3._h3_cuogz_1').text.strip()
                descriprion_contents= step.select_one('div.articleContent._articleContent_kc5qn_216 div._summary_kc5qn_21 p')
                destination_rank=re.findall(r'\d+',ranking_number)[0]
                destination_name =' '.join(re.findall(r'[a-zA-Z]+', step_name))
                #print(destination_rank, destination_name)
                if descriprion_contents:
                    descriprion_contents=descriprion_contents.get_text()
                    #print(descriprion_contents)               
                # Store the data in a dictionary
                step_data = {
                    "month_name": month_link[0],
                    "ranking_number": destination_rank,
                    "destination_name": destination_name,
                    "description_text": descriprion_contents
                    ,"destination_url": ulr_destination
                }
                
                # Add the step data to the  container
                Datacontainer.append(step_data)  
    except ValueError as val_err:
        print(f'Value error occurred: {val_err}')  # Handle the empty URL case
    except TypeError as type_err:
        print(f'There is a format error:{type_err}')    
    except RequestException as req_err:
        print(f'Request error occurred: {req_err}')  # Handle all requests-related exceptions
        

    return Datacontainer




def ReadingFromJson(sourcejsn):
    '''
    function to read from jason file which is 'travel_destinations.json' here
    '''
    DataContainer=[]
    try:
            with open(sourcejsn, 'r') as fh: 
                    try:
                             
                            DataContainer = json.load(fh)
                            
                    except StopIteration :
                            raise json.JSONDecodeError("JSONDecodeError ") from None 
    except FileNotFoundError as err:
            print(f'File {sourcejsn} not found : {err}')
    except json.JSONDecodeError:
            print(f'There is no Data in json file')
    return DataContainer

def creatDb(DataContainer):
    '''
    function to creat data base end write on suitable format based on the json file
    '''    
    
    #DataContainer=[{ "month_name": "January","ranking_number": "1","destination_name": "Melbourne",
    #"description_text": "Live in the Northern Hemisphere? Cancel winter\u2019s contract and go ....,
    #"destination_url": "https://www.timeout.com/melbourne" },...]         
    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect('TravelDestination.db')
    cur = conn.cursor()
    
    # Create the Months table
    cur.execute("DROP TABLE IF EXISTS Months")
    cur.execute('''
        CREATE TABLE Months (
            id INTEGER NOT NULL PRIMARY KEY,
            month TEXT UNIQUE ON CONFLICT IGNORE)''')
    
    # Create the CityInfo table
    cur.execute("DROP TABLE IF EXISTS CityInfo")
    cur.execute('''
        CREATE TABLE CityInfo (
            cid INTEGER NOT NULL PRIMARY KEY UNIQUE,
            name TEXT,
            rank INTEGER,
            month_id INTEGER,
            description TEXT,
            destination_url TEXT,
            FOREIGN KEY (month_id) REFERENCES Months(id))''')
    
    # Insert data from DataContainer into the database
    for record in DataContainer:
        
             
            # Check if the month already exists in the Months table
            cur.execute('SELECT id FROM Months WHERE month = ?', (record["month_name"],))
            result = cur.fetchone()
            if result:
                    month_id = result[0]
            else:
                    # Insert the month into the Months table and retrieve the new month_id
                    cur.execute('INSERT INTO Months (month) VALUES (?)', (record["month_name"],))
                    cur.execute('SELECT id FROM Months WHERE month = ?', (record["month_name"],))
                    month_id = cur.fetchone()[0]
        
            # Insert data into the CityInfo table
            cur.execute('''
                INSERT INTO CityInfo (name, rank, month_id, description, destination_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (record["destination_name"], int(record["ranking_number"]), month_id, record["description_text"], record["destination_url"]))
    
    # Commit the transaction
    conn.commit()
    
    # Close the connection
    conn.close()
    
    print("Writing to the database was successful.")
         
#######main start from here
data=[]

#siteurl = 'https://www.timeout.com/things-to-do/best-places-to-travel'
#data=ScrapeData(data,siteurl)


#this part of code write to json file if uncomment
'''
with open('travel_destinations.json', 'w', encoding='utf-8') as f: 
         
        json.dump(data,f,indent=1)

print("Data has been successfully scraped and saved to travel_destinations.json")
'''

sourcejsn='travel_destinations.json'  
#call function to read data and write in json
data=ReadingFromJson(sourcejsn)
#print data for test 

for city in data: 
   
    print("Month:",city['month_name'].upper(),"City Rank:",city['ranking_number'].upper(),"Destination:",city['destination_name'].upper())
    print("-----------------------------------------------------")
    print("The URL of city:",city['destination_url'])
    print("Descrtion:\n",city['description_text'])
    print()

#call function to read from json and write in Db
creatDb(data)

