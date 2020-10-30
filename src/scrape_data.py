import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

#set up Mongo to store data 
client = MongoClient('localhost', 27017)

db = client['cap1_db']
col1 = db['col1']
col_people = db['col_people']

%run scraping_functions.py

category_url = ['Data_scientists', 
                '20th-century_economists',
                '21st-century_economists', 
                '21st-century_chemists', 
                '20th-century_chemists',
                '21st-century_physicists',
                '20th-century_physicists',
                '21st-century_biologists',
                '20th-century_biologists',
                'Microbiologists',
                '21st-century_physicians',
                '20th-century_physicians']


for i in category_url: 
    # save html to doc
    html_to_collection(col1, i)
    #add list of names and links to doc
    people_to_collection(col1, i)
    #add list of subcategories to doc
    find_subcategories(col1, i)
    #grab list of names from the next page if there is one
    names_on_next_page(col1, i)



# Subcategories 
subcategory_url = set()
write_subcategories_to_set(col1, subcategory_url)

subcategory_old = set()
subcat_rounds = 0

while subcat_rounds < 2: 

    only_new_subcats = subcategory_url.difference(subcategory_old)
    
    for i in only_new_subcats: 
        # save html to doc
        html_to_collection(col1, i)
        #add list of names and links to doc
        people_to_collection(col1, i)
        #add list of subcategories to doc
        find_subcategories(col1, i)
        #grab list of names from the next page if there is one
        names_on_next_page(col1, i)
        
    subcategory_old.update(only_new_subcats)
    write_subcategories_to_set(col1, subcategory_url)
            
    subcat_rounds +=1


#Clean weird subcategories 
col1.delete_many({"page": {"$regex": 'Taxa?'}})
col1.delete_many({"page": {"$regex": 'Books?'}})
col1.delete_many({"page": {"$regex": 'Fictional?'}})
col1.delete_many({"page": {"$regex": 'Bloomsbury?'}})
col1.delete_many({"page": {"$regex": '\_Nazi?'}})
col1.delete_many({"page": 'Antonie_van_Leeuwenhoek'})
col1.delete_many({"page": 'Max_Planck'})
col1.delete_many({"page": 'Friedrich_Hayek'})
col1.delete_many({"page": {"$regex": '\Friedman?'}})
col1.delete_many({"page": 'Max_Planck'})
col1.delete_many({"page": 'Marie_Curie'})
col1.delete_many({"page": 'B._R._Ambedkar'})
col1.delete_many({"page": 'Richard_Feynman'})
col1.delete_many({"page": 'Werner_Heisenberg'})
col1.delete_many({"page": 'Virginia_Woolf'})
col1.delete_many({"page": 'Amartya_Sen'})
col1.delete_many({"page": 'Strachey_family'})
col1.delete_many({"page": 'Cultural_depictions_of_Marie_Curie'})
col1.delete_many({"page": 'Curie_family'})
col1.delete_many({"page": 'Robin_F%C3%A5hr%C3%A6us'})
col1.delete_many({"page": 'Manmohan_Singh'})
col1.delete_many({"page": 'E._M._Forster'})
col1.delete_many({"page": 'John_Maynard_Keynes'})



list_all_pages = []
for doc in col1.find():
    page = doc['page']
    list_all_pages.append(page)

print(f"There are {len(list_all_pages)} documents")


#People to new collection
progress = 0
for page in list_all_pages:
    progress += 1
    print(f"{progress}: {page}")
    people_html_to_collection(col1, page, col_people)


list_all_people = []
for doc in col_people.find():
    page = doc['page']
    list_all_people.append(page)

print(f"There are {len(list_all_people)} people")


progress = 0
hundred = 0
for person in list_all_people:
    progress +=1 
    count_gendered_words(col_people, person)
    if progress == 100:
        hundred += 1
        print(f"{hundred}: {person}: another 100" )
        progress = 0


num_ppl = 0 
for doc in col_people.find():
    num_ppl +=1
    
num_ppl

df = pd.DataFrame(col_people.find())
df_tocsv = df[['page', 'field', 'count_female_words', 'count_male_words', 'count_nonbinary_words', 'doctorate', 'len_page']]
df_tocsv.to_csv('data/wiki_profile.csv')