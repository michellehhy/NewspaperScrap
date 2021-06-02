import requests
from bs4 import BeautifulSoup
import feedparser
from pandas import json_normalize
import pandas as pd


url = 'https://www.bbc.co.uk/news/health-48581317'

#Request the article url to get the web page content.
article = requests.get(url)
soup = BeautifulSoup(article.content, 'html.parser')

##Get main body
# 1. extract all paragraph elements inside the page body
articles_body = soup.findAll('body')    
p_blocks = articles_body[0].findAll('p')

# 2. for each paragraph, construct its patents elements hierarchy
#Create a dataframe to collect p_blocks data
p_blocks_df=pd.DataFrame(columns=['element_name','parent_hierarchy','element_text','element_text_Count'])
for i in range(0,len(p_blocks)):
  
  # 2.1 Loop trough paragraph parents to extract its element name and id
  parents_list=[]
  for parent in p_blocks[i].parents:
    
    #Extract the parent id attribute if it exists
    Parent_id = ''
    try:
      Parent_id = parent['id']
    except:
      pass
    
    # Append the parent name and id to the parents table
    parents_list.append(parent.name + 'id: ' + Parent_id)
  
  # 2.2 Construct parents hierarchy
  parent_element_list = ['' if (x == 'None' or x is None) else x for x in parents_list ]
  parent_element_list.reverse()
  parent_hierarchy = ' -> '.join(parent_element_list)
  
  #Append data table with the current paragraph data
  p_blocks_df=p_blocks_df.append({"element_name":p_blocks[i].name
                                  ,"parent_hierarchy":parent_hierarchy
                                  ,"element_text":p_blocks[i].text
                                  ,"element_text_Count":len(str(p_blocks[i].text))}
                                  ,ignore_index=True
                                  ,sort=False)
    
  # 3. concatenate paragraphs under the same parent hierarchy
if len(p_blocks_df)>0:
    p_blocks_df_groupby_parent_hierarchy=p_blocks_df.groupby(by=['parent_hierarchy'])
    p_blocks_df_groupby_parent_hierarchy_sum=p_blocks_df_groupby_parent_hierarchy[['element_text_Count']].sum()            
    p_blocks_df_groupby_parent_hierarchy_sum.reset_index(inplace=True)            

# 4. count paragraphs length
# 5. select the longest paragraph as the main article
maxid=p_blocks_df_groupby_parent_hierarchy_sum.loc[p_blocks_df_groupby_parent_hierarchy_sum['element_text_Count'].idxmax()
                                                     ,'parent_hierarchy']
merge_text='\n'.join(p_blocks_df.loc[p_blocks_df['parent_hierarchy']==maxid,'element_text'].to_list())

print(merge_text)

##get Title
title = soup.find("meta",  {"property":"og:title"}).get('content')

# date
date = soup.find("meta",  {"property":"article:published_time"}).get('content')

# description
description = soup.find("meta", {"property":"og:description"}).get('content')

# keyword
keywords = []
keyword = soup.findAll("meta",  {"property":"article:tag"})
for k in keyword:
  keywords.append(k["content"] if k else None)
# wordcount
wordcount = soup.find("meta",  {"property":"article:word_count"}).get('content')

print("title: ", title)
print("description: ", description)
print("date: ",date)
print("keywords: ",keywords)
print("wordcount: ",wordcount)
