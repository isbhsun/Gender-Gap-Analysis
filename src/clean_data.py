#set directory 
file_path = '/Users/isabella/gal/capstone/Gender-Gap-Analysis/'

import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import pandas as pd

#set up Mongo to store data 
client = MongoClient('localhost', 27017)

db = client['cap1_db']
col1 = db['col1']
col_people = db['col_people']

#origin category list for iterating
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


#create dictionary of subcategories so we can assign each profile to the appropriate broader category and field
subcat_dict = dict()
for i in category_url:
    doc = col1.find_one({'page': i })
    subcat_dict[i] = doc['subcat_link']
    
subcat_dict2 = dict()
subcategory_category_url = []
for i in category_url: 
    doc = col1.find_one({'page': i})
    subcat_list = doc['subcat_link']
    for subcat in subcat_list:
        subcat = subcat.replace('/wiki/Category:', '')
        subcategory_category_url.append(subcat)
        subdoc = col1.find_one({'page': subcat })
        try:
            subcat_dict2[subcat] = subdoc['subcat_link']
        except:
            subcat_dict2[subcat] = None

full_subcat_dict = {}
for k, v in subcat_dict.items():
    for cat in v:
        cat = cat.replace('/wiki/Category:', '')
        for k2, v2 in subcat_dict2.items():
            if cat == k2:
                sub_dict = {k2:v2}
                if k not in full_subcat_dict:
                    full_subcat_dict[k] = sub_dict
                elif k in full_subcat_dict:
                    full_subcat_dict[k].update(sub_dict)

for k, v in full_subcat_dict.items():
    for k2, v2, in full_subcat_dict[k].items():
        fix_list = []
        try:
            for cat in v2:
                cat = cat.replace('/wiki/Category:', '')
                fix_list.append(cat)
        except:
            continue
        full_subcat_dict[k][k2] = fix_list

flat_dict = {}
for k, v in full_subcat_dict.items():
    flatten = []
    for k2, v2 in v.items():
        flatten.append(k2)
        try:
            for i in v2:
                flatten.append(i)
        except:
            continue
    flat_dict[k] = flatten

#dictionary of origin categories to fields
category_field_dict = {'Data Science': ['Data_scientists'] , 
            'Economics': ['20th-century_economists',
                '21st-century_economists'],
           'Chemistry': ['21st-century_chemists', 
                '20th-century_chemists'] ,
           'Physics' : ['21st-century_physicists',
                '20th-century_physicists'] ,
           'Physiology or Medicine' : ['21st-century_biologists',
                '20th-century_biologists',
                'Microbiologists',
                '21st-century_physicians',
                '20th-century_physicians']}


def invert_dictionary(d):
    d_out = dict()
    for k, v in d.items():
        for val in v:
            if val not in d_out:
                d_out[val] = set()
                d_out[val]= k
    return d_out

def merge_dictionaries(d1, d2):

    d = d1.copy()
    for key, value in d2.items():
        if key in d:
            continnue
        else:
            d[key] = key
    return d


field_dct = invert_dictionary(flat_dict)

d_original = {}
d_original = d_original.fromkeys(category_url)

field_dct = merge_dictionaries(field_dct, d_original)
origin_category = invert_dictionary(category_field_dict)



# Clean data and create key variables 
wik_profiles_toclean = pd.read_csv(file_path+'data/wiki_profile.csv')
wik_profiles_toclean = wik_profiles_toclean.drop('Unnamed: 0',1)
wik_profiles_toclean.reset_index()

#make sure data types are appropriate 
wik_profiles_toclean[['count_female_words', 'count_male_words', 'count_nonbinary_words', 'len_page']].astype(int)
wik_profiles_toclean['doctorate'].astype(bool)


# Generate Gender columns from word counts 
wik_profiles_toclean['female'] = [True if x > y              
                   else False 
                   for x, y in zip(wik_profiles_toclean['count_female_words'], wik_profiles_toclean['count_male_words'])]

wik_profiles_toclean['male'] = [True if y > x                   
                   else False 
                   for x, y in zip(wik_profiles_toclean['count_female_words'], wik_profiles_toclean['count_male_words'])]
wik_profiles_toclean['gender_unclear'] = [True if y == x                   
                   else False 
                   for x, y in zip(wik_profiles_toclean['count_female_words'], wik_profiles_toclean['count_male_words'])]

wik_profiles_toclean[['female', 'male', 'gender_unclear']].sum()

non_binary = wik_profiles_toclean[wik_profiles_toclean['gender_unclear']==True]
#where gender is unclear, it appears that these profiles tend to be in another language or are too short
#for example: https://en.wikipedia.org/wiki/Ren%C3%A9_Courtin
#https://en.wikipedia.org/wiki/Auguste_Det%C5%93uf
# https://en.wikipedia.org/wiki/Jules_L%C3%A9on_Austaut

#Keep profiles where gender can be determined from the counts of gendered words in wikipedia profile
wik_profiles = wik_profiles_toclean[wik_profiles_toclean['gender_unclear']==False].copy()


#Use previously created dictionaries to label each profile with the appropriate field and broader category

category = []
here = []
for field in wik_profiles['field']:
    if field in field_dct:
        category.append(field_dct[field])
        here.append(1)
    else:
        category.append(field)
        here.append(0)

wik_profiles['category'] = category
wik_profiles['count'] = here

field = []
for category in wik_profiles['category']:
    if category in origin_category:
        field.append(origin_category[category])

    else:
        print("why don't i exist?")

wik_profiles['nobel_field'] = field

df_analysis = wik_profiles[['page', 'doctorate', 'len_page', 'female', 'male', 'category', 'count', 'nobel_field']]

df_analysis.to_csv(file_path+'data/wiki_profile_cleaned.csv')