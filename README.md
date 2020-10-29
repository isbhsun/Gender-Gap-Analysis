# Introduction

The goal of this project is to measure the gender gap in various fields using scraped data from wikipedia. 

Rather than measuring the proportion of women in a field, this analysis looks specifically at individuals at the top of their field, the assumption being that individuals with a wikipedia page are somewhat notable figures. 

It is important to acknowledge that there are more than two genders. Due to data constraints, for this project, I examine the difference between only men and women in a field. 


# Data
 
## Creating the Dataset

To acquire this data, I scraped wikipedia pages to create a novel dataset. Using the Requests library and BeautifulSoup, I grabbed the profiles of individuals listed under relevant categories and saved the information into a Mongo database. I chose to focus on categories relevant to the Nobel Prize fields (i.e. physics, chemistry, physiology or medicine, literature, peace, and economics), then narrowed it down to economics and STEM fields. I excluded literature categories because the categories were too vast for the time constraints of this project. I similarly excluded the peace category because winners of the peace category generally come from a broad range of fields making it difficult to categorize. Data scientists is the one non-Nobel category included out of personal interest.  

The origin categories I chose were:
- [Data Scientists](https://en.wikipedia.org/wiki/Category:Data_scientists)
- [20th Century Economists](https://en.wikipedia.org/wiki/Category:20th-century_economists)
- [21st Century Economists](https://en.wikipedia.org/wiki/Category:21st-century_economists)
- [20th Century Chemists](https://en.wikipedia.org/wiki/Category:20th-century_chemists)
- [21st Century Chemists](https://en.wikipedia.org/wiki/Category:21st-century_chemists)
- [20th Century Physicists](https://en.wikipedia.org/wiki/Category:20th-century_physicists)
- [21st Century Physicists](https://en.wikipedia.org/wiki/Category:21st-century_physicists)
- [20th Century Biologists](https://en.wikipedia.org/wiki/Category:20th-century_biologists)
- [21st Century Biologists](https://en.wikipedia.org/wiki/Category:21st-century_biologists)
- [Microbiologists ](https://en.wikipedia.org/wiki/Category:Microbiologists)
- [20th Century Physicians](https://en.wikipedia.org/wiki/Category:20th-century_physicists)
- [21st Century Physicians](https://en.wikipedia.org/wiki/Category:21st-century_physicists)

Most categories on wikipedia have subcategories, and individuals listed underneath a category might not be tagged in a subcategory and visa versa. For example, [Paul Krugman](https://en.wikipedia.org/wiki/Paul_Krugman) is not listed under 21st Century Economists, but is listed under the subcategory, 21st Century American Economists. Given the imperfect nature of the wikipedia tags and categories, I also included all individuals listed under 2 levels of subcategories from the original categories. 

Once I scraped the names and links of individuals under each category and subcategory, I scraped the body text of their profiles and used the information in the text to determine their gender, length of their profile, and whether they held a doctorate. 


## Data Description 



# Analysis 



# Conclusion 