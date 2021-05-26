import requests
from bs4 import BeautifulSoup
from newspaper import Article
from newspaper import fulltext
import json
import pandas as pd


# get links from rss feed and save as csv
def healthnews_rss(url='https://www.inoreader.com/stream/user/1004791332/tag/user-favorites?n=100'):
    article_list = []   
    frame = []
    upper_frame = []
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, features='xml')

        articles = soup.findAll('item')
        for a in articles:
            # title = a.find('title').text
            link = a.find('link').text
            # published = a.find('pubDate').text
            # outlet = a.find('dc:creator').text
            # article = {
            #     'title': title,
            #     'link': link,
            #     'published': published,
            #     'outlet': outlet
            #     }
            article_list.append(link)  

        return save_function(article_list)

    except Exception as e:
        print(e)
        
    
    # filename = "news.csv"
    # f=open(filename,"w", encoding = 'utf-8')
    # headers="title ,Link, Date, Source\n"
    # f.write(headers)

def save_function(article_list):
    with open('articles.csv', 'w') as f:
        for a in article_list:
            f.write(a+'\n')
#             article = Article(a)
#             article.download()
#             article.parse()
#             article.nlp()
#             html = requests.get(a).text
#             text = fulltext(html)
#             f.write(text+'\n') 
            # f.write(article.title)
            # f.write(article.publish_date)
            # f.write(article.authors)
            # f.write(article.keywords)
        f.close()

      

print('Starting scraping')
healthnews_rss()
print('Finished scraping')
