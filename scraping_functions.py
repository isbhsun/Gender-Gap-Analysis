def html_to_collection(collection, page):
    
    doc = collection.find_one({'page': page })    
    try:
        doc['page']
        print(f"{page} page already exists!")
    
    except:
        wik = 'https://en.wikipedia.org/wiki/Category:'
        url = wik + page
        r = requests.get(url)
        collection.insert_one({'page': page, 
                               'html':r.content})
        print(f"{page}: I saved the html")
        
    return None 


def people_to_collection(collection, page):
    
    doc = collection.find_one({'page': page })
    
    try:
        doc['list_names']
        print(f"{page} names already here!")
    
    except:
        try:

            soup = BeautifulSoup(doc['html'] ,'html.parser')
            div = soup.find("div", {'class':'mw-category'})

            list_link_ext = []
            for link in div.find_all('a'):
                list_link_ext.append(link['href'])
            print(f"{page}:i grabbed a person link!")

            #grab names
            list_names = []
            for link in div.find_all('a'):
                list_names.append(link['title'])
            print(f"{page}:i grabbed a name!")

            collection.update_one({'page': page },{"$set":{'list_names': list_names,
                                                          'list_name_links': list_link_ext
                                                         }})
        except: 
            print(f"{page} oh no i couldn't find people")
        return None


def find_subcategories(collection, page):
    
    doc = collection.find_one({'page': page })
    
    try:
        doc['subcat_name']
        print(f"{page} subcategories already here!")
    
    except:
        try:
            soup = BeautifulSoup(doc['html'] ,'html.parser')

            div = soup.find("div", {'id':'mw-subcategories'})

            subcat_link = []
            for link in div.find_all('a'):
                subcat_link.append(link['href'])
            print(f"{page}: i added a subcategory link")

            subcat_name = []
            for link in div.find_all('a'):
                subcat_name.append(link['title'])
            print(f"{page}: i added a subcategory name")

            collection.update_one({'page': page },{"$set":{'subcat_name': subcat_name,
                                                          'subcat_link': subcat_link
                                                         }})
        except:
            print(f"{page}: I have no subcategories")
        return None
        


def find_next_page(collection, page):
    
    doc = collection.find_one({'page': page })
    
    try:
        doc['next_page']
        print(f"{page}: next page already here!")
    
    except:
        try:
            soup = BeautifulSoup(doc['html'] ,'html.parser')
            div = soup.find("div", {'id':'mw-pages'})   

            links = []
            for link in div.find_all('a'):
                links.append(link['href'])

            last_link = links.pop()
            if 'pagefrom' in last_link:
                collection.update_one({'page': page },{"$set":{'next_page': last_link}})
                print(f"{page}:I grabbed the next page")
            else:
                print(f"{page}:I'm already the last page")    
        
        except:
            collection.update_one({'page': page },{"$set":{'next_page': 'only page'}})
            print(f"{page}: I'm the only page")
    
    return None


def subcat_html_to_collection(collection, page):
    
    doc = collection.find_one({'page': page })
    
    try: 
        subcat_link = doc['subcat_link']
        wik = 'https://en.wikipedia.org/'

        for i in subcat_link:
            url = wik + i
            r = requests.get(url)
            subcat_page = i.replace('/wiki/Category:', '')

            if subcat_page in subcategory_url:
                print(f"{subcat_page}: subcategory html already here")
            elif subcat_page not in subcategory_url:
                subcategory_url.add(subcat_page)
                collection.insert_one({'page': subcat_page, 
                               'html':r.content})
                print(f"{subcat_page}: I saved the subcat html")

    except:
        print(f"{page} I don't have subcategories or they are already added")



def count_gendered_words(collection, person):
    
    doc = col_people.find_one({'page': person })
    
    try:
        doc['count_female_words']
        print(f"{person}: words already counted")
    
    except: 
        soup = BeautifulSoup(doc['html'], 'html.parser')
        div = soup.find("div", {'id':'mw-content-text'})

        substring_female = [' she ', ' her ']
        substring_male = [' he ', ' his ']
        substring_nonbinary = [' they ', ' them ', 'ze ', ' zir ', ' hir ']

        count_female_words = 0
        for word in substring_female:
            count = str(div).lower().count(word)
            count_female_words += count

        count_male_words = 0
        for word in substring_male:
            count = str(div).lower().count(word)
            count_male_words += count
            
        count_nonbinary_words = 0
        for word in substring_nonbinary:
            count = str(div).lower().count(word)
            count_nonbinary_words += count


        col_people.insert_one({'count_female_words': count_female_words, 
                            'count_male_words': count_male_words,
                            'count_nonbinary_words': count_nonbinary_words})
        print(f"{person}: female {count_female_words}, male {count_male_words}, nonbinary {count_nonbinary_words}")
    
    return None

    
def people_html_to_collection(col_from, page, col_to):
    doc = col_from.find_one({'page': page })
    links = doc['list_name_links']
    names = doc['list_names']

    for link, name in zip(links, names):
        doc_person = col_to.find_one({'page': name })

        try:
            doc_person['page']
            print(f"{name}: page already exists!")

        except:
            wik = 'https://en.wikipedia.org'
            url =  wik + link
            r = requests.get(url)
            col_to.insert_one({'page': name, 
                               'field': page
                                'html':r.content})
            print(f"{name}: I saved the html")
            
        try:
            count_gendered_words(col_to, name)
        except:
            print("oops")

    return None
