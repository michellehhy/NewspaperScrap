import requests
from bs4 import BeautifulSoup
from newspaper import Article
import json
import pandas as pd
import time

def healthnews_rss(url='https://www.inoreader.com/stream/user/1004791332/tag/user-favorites?n=110'):
    article_list = []   
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, features='xml')

        articles = soup.findAll('item')
        for a in articles:
            link = a.find('link').text
            article_list.append(link)  

        return scrap_fulltext(article_list)

    except Exception as e:
        print(e)
        

def scrap_fulltext(article_list):
    text_list = []
    for a in article_list:
        article = requests.get(a)

        # 1. extract all paragraph elements inside the page body
        articles = BeautifulSoup(article.content, 'html.parser')
        articles_body = articles.findAll('body')    
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
        maxid=p_blocks_df_groupby_parent_hierarchy_sum.loc[p_blocks_df_groupby_parent_hierarchy_sum['element_text_Count'].idxmax(),'parent_hierarchy']
        merge_text=' '.join(p_blocks_df.loc[p_blocks_df['parent_hierarchy']==maxid,'element_text'].to_list())
        
        # news = Article(a)
        # news.download()
        # news.parse()
        # title = news.title
        # author = news.authors
        # pub_date = news.publish_date
        # news.nlp()
        # keywords = news.keywords
        # summary = news.summary
        
        entry = {'link': a,
                #  'title': title,
                #  'author': author,
                #  'date': pub_date,
                #  'keywords': keywords,
                #  'summary': summary,
                 'text': merge_text}
        text_list.append(entry)
    
    df = pd.DataFrame(text_list)
    df.to_csv('text_list2.csv', index = False)
#     return save_full_text(text_list)
       
 
# def save_full_text(text_list):
#     with open('text.csv', 'w') as f:
#         for a in text_list:
#             f.write(a)
#         f.close()        


print('Starting scraping')
start_time = time.time()
healthnews_rss()
print('Finished scraping')
print("--- %s seconds ---" % (time.time() - start_time)) 
