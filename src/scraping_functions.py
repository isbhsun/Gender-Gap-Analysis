import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import pandas as pd
import re
import string
from collections import Counter


def html_to_collection(collection, page):

    doc = collection.find_one({'page': page})
    try:
        doc['page']
        print(f"{page} page already exists!")

    except:
        wik = 'https://en.wikipedia.org/wiki/Category:'
        url = wik + page
        r = requests.get(url)
        collection.insert_one({'page': page,
                               'html': r.content})
        #  print(f"{page}: I saved the html")

    return None


def people_to_collection(collection, page):

    doc = collection.find_one({'page': page})

    try:
        doc['list_names']
        #  print(f"{page} names already here!")

    except:
        try:
            soup = BeautifulSoup(doc['html'], 'html.parser')
            div = soup.find("div", {'id': 'mw-pages'})

            list_link_ext = []
            list_names = []

            for link in div.find_all('a'):
                list_link_ext.append(link['href'])
                list_names.append(link['title'])

            #  print(f"{page}: i grabbed a person and link!")
            collection.update_one({'page': page}, {"$set": {
                'list_names': list_names,
                'list_name_links': list_link_ext}})
        except:
            print(f"{page} oh no i couldn't find people")
    return None


def find_subcategories(collection, page):

    doc = collection.find_one({'page': page})

    try:
        doc['subcat_link']
        #  print(f"{page} subcategories already here!")

    except:
        try:
            soup = BeautifulSoup(doc['html'], 'html.parser')

            div = soup.find("div", {'id': 'mw-subcategories'})

            subcat_link = []
            for link in div.find_all('a'):
                subcat_link.append(link['href'])
            #  print(f"{page}: i added a subcategory link")

            collection.update_one({'page': page}, {"$set": {
                'subcat_link': subcat_link}})

        except:
            print(f"{page}: I have no subcategories")
    return None


def names_on_next_page(collection, page):

    doc = collection.find_one({'page': page})

    try:
        doc['last_page']
        #  print('already looked for all the pages')

    except:
        try:
            orig_names_list = doc['list_names']
            orig_links_list = doc['list_name_links']

            soup = BeautifulSoup(doc['html'], 'html.parser')
            div = soup.find("div", {'id': 'mw-pages'})

            wik = 'https://en.wikipedia.org/'

            last_page = False
            while last_page is False:

                last_link = orig_links_list[-1]

                if 'pagefrom' in last_link:

                    orig_links_list.pop()

                    ext = last_link
                    url = wik + ext
                    #  print(f"not last {url}")

                    r = requests.get(url)
                    soup = BeautifulSoup(r.content, 'html.parser')
                    div = soup.find("div", {'id': 'mw-pages'})

                    for link in div.find_all('a'):
                        orig_links_list.append(link['href'])
                        orig_names_list.append(link['title'])

                else:
                    collection.update_one({'page': page}, {"$set": {
                        'list_names': orig_names_list,
                        'list_name_links': orig_links_list,
                        'last_page': 'last_page'}})
                    last_page = True
        except:
            print(f"{page}: something went wrong")
    return None


def write_subcategories_to_set(collection, subcategory_set):

    wik = 'https://en.wikipedia.org/'

    num_subcategories_added = 0
    for doc in collection.find():
        try:
            for i in doc['subcat_link']:
                url = wik + i
                r = requests.get(url)
                subcat_page = i.replace('/wiki/Category:', '')

                if subcat_page in subcategory_set:
                    continue
                elif subcat_page not in subcategory_set:
                    subcategory_set.add(subcat_page)
                    num_subcategories_added += 1
        except:
            continue
    return num_subcategories_added


def count_gendered_words(collection, person):

    doc = collection.find_one({'page': person})

    try:
        doc['count_female_words']
        #  print(f"{person}: words already counted")

    except:

        str_body_text = doc['body_text']
        str_body_text_2 = str(str_body_text).lower()

        #  years = re.findall('\d\d\d\dD?', str_body_text)
        list_words_in_body = str_body_text_2.split(' ')
        dct_word_counter = Counter(list_words_in_body)

        count_female_words = (dct_word_counter['she'] +
                              dct_word_counter['her'] +
                              dct_word_counter['hers'])
        count_male_words = (dct_word_counter['he'] +
                            dct_word_counter['him'] +
                            dct_word_counter['his'])
        count_nonbin_words = (dct_word_counter['they'] +
                              dct_word_counter['them'] +
                              dct_word_counter['theirs'] +
                              dct_word_counter['ze'] +
                              dct_word_counter['zir'] +
                              dct_word_counter['hir'])

        collection.update_one({'page': person}, {"$set": {
            'count_female_words': count_female_words,
            'count_male_words': count_male_words,
            'count_nonbinary_words': count_nonbin_words,
            'len_page': len(list_words_in_body),
            'word_dict': dct_word_counter}})

    return None


def people_html_to_collection(col_from, page, col_to):

    try:
        doc = col_from.find_one({'page': page})
        links = doc['list_name_links']
        names = doc['list_names']

        for link, name in zip(links, names):
            doc_person = col_to.find_one({'page': name})

            try:
                doc_person['page']

            except:
                wik = 'https://en.wikipedia.org'
                url = wik + link
                r = requests.get(url)
                col_to.insert_one({'page': name,
                                   'field': page,
                                   'html': r.content})

            try:
                just_body_text(col_to, name)
            except:
                print(f"{page}: oops body text")

    except:
        print(f"{page}: oops... not sure")
    return None


def just_body_text(collection, person):

    doc = collection.find_one({'page': person})

    try:
        doc['body_text']

    except:

        soup = BeautifulSoup(doc['html'], 'html.parser')
        div = soup.find("div", {'class': 'mw-parser-output'})

        body = str(div)
        body_text = re.sub('<[^>]+>', '', body)

        if "Ph.D" in body_text:
            doctorate = 1
        else:
            doctorate = 0

        punct = string.punctuation
        for char in punct:
            body_text = body_text.replace(char, ' ')
        body_text = body_text.replace('\n', ' ')
        body_text = body_text.replace('\xa0', ' ')

        collection.update_one({'page': person}, {"$set": {
            'body_text': body_text,
            'doctorate': doctorate}})
    return None


if __name__ == "__main__":

    client = MongoClient('localhost', 27017)

    db = client['scrape_test_db']
    categories_col = db['categories_col']
    people_col = db['people_col']

    #  save html to doc
    html_to_collection(categories_col, 'Data_scientists')
    #  add list of names and links to doc
    people_to_collection(categories_col, 'Data_scientists')
    #  add list of subcategories to doc
    find_subcategories(categories_col, 'Data_scientists')
    #  grab list of names from the next page if there is one
    names_on_next_page(categories_col, 'Data_scientists')

    subcategory_url = set()
    write_subcategories_to_set(categories_col, subcategory_url)

    for i in subcategory_url:
        #   save html to doc
        html_to_collection(categories_col, i)
        #  add list of names and links to doc
        people_to_collection(categories_col, i)
        #  add list of subcategories to doc
        find_subcategories(categories_col, i)
        #  grab list of names from the next page if there is one
        names_on_next_page(categories_col, i)

    list_all_pages = []
    for doc in categories_col.find():
        page = doc['page']
        list_all_pages.append(page)

    print(f"There are {len(list_all_pages)} documents")

    progress = 0
    for page in list_all_pages:
        progress += 1
        print(f"{progress}: {page}")
        people_html_to_collection(categories_col, page, people_col)

    list_all_people = []
    for doc in people_col.find():
        page = doc['page']
        list_all_people.append(page)

    progress = 0
    hundred = 0
    for person in list_all_people:
        progress += 1
        count_gendered_words(people_col, person)
        if progress == 100:
            hundred += 1
            print(f"{hundred}: {person}: another 100")
            progress = 0
