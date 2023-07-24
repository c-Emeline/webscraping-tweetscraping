'''

Gather data from the press (and social media) regarding positive and negative aspects of Elon Musk 
to enable a later semantic analysis of global opinions about Elon Musk.

'''


#1. BBC website


import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import sqlite3



linkSelectedBBC = []
articleDateBBC = []
articleHourBBC = []
articleTitleBBC = []
articleTextBBC = []
articleKeyWordBBC = []

n1=0


#Select the links of articles (which are not programmes) 30 first pages
for i in range(30):
    
    page = requests.get("https://www.bbc.co.uk/search?q=elon+musk&page="+str(i))

    soupe = BeautifulSoup(page.text, 'html.parser')

    articleList = soupe.find(attrs = {'class' : 'ssrcss-1020bd1-Stack e1y4nx260'})
        
    if articleList!=None :
        articlePage = articleList.find_all('a') 
    
        for article in articlePage:
        
            #Excluding the links leading to programmes
            if not(re.search('/programmes/', article.get('href'))) and not(re.search('/newsround/', article.get('href'))):
                linkSelectedBBC.append(article.get('href'))



#Get information about each article (through their links)
for link in linkSelectedBBC :
    
    page = requests.get(link)
    soupe = BeautifulSoup(page.text, 'html.parser')
    
    #Get article's date/hour
    datetime = soupe.find('time')['datetime']

    date = re.search('^[0-9]{4}-[0-9]{2}-[0-9]{2}', datetime)
    hour = re.search('[0-9]{2}:[0-9]{2}:[0-9]{2}', datetime)
    
    #Get article's title
    title = soupe.find(attrs = {'id' : 'main-heading'}).text
    
    #Get article text content
    textContent = soupe.findAll(attrs = {'class' : 'ssrcss-1q0x1qg-Paragraph eq5iqo00'})
    
    #Get article's key words
    keyWordList = soupe.find(attrs = {'class' : 'ssrcss-d7aixc-ClusterItems e1ihwmse0'})
    
    #If all the data has been found, store it in the lists
    if date and hour and title!=None and textContent!=None and textContent!=[] : 
        articleDateBBC.append(date.group(0))
        articleHourBBC.append(hour.group(0))
        articleTitleBBC.append(title)
        
        wholeText=''
        for content in textContent :
            #exclude unwanted text content
            if content.text not in ['Â© 2022 BBC. The BBC is not responsible for the content of external sites. Read about our approach to external linking.', 'This video can not be played', 'Martin Kemp and Lady Leshurr are out to prove age is just a number', 'Fri Martin was jailed for her boyfriend\'s murder. Now she is appealing her conviction...', 'Why are we still captivated by these mythological beasts?'] :
                wholeText += content.text + ' '
        articleTextBBC.append(wholeText)
        
        #If key words are found, store it, else store None
        if keyWordList != None :
            keyWords = []
            for keyWord in keyWordList :
                keyWords.append(keyWord.text)
            articleKeyWordBBC.append(keyWords)
        else :
            articleKeyWordBBC.append(["None"])

        n1+=1
        


articleMediaBBC = ['bbc']*n1

#Pandas dataframe creation
bbcDf = pd.DataFrame({'media' : articleMediaBBC, 'url' : linkSelectedBBC, 'title' : articleTitleBBC, 'date' : articleDateBBC, 'hour' : articleHourBBC, 'text' : articleTextBBC, 'key_word' : articleKeyWordBBC})

bbcDf.to_csv('BbcElonMusk1.csv')



#2. Times website


nb_page = 10

articleLinkTimes = []
articleTitleTimes = []
articleDateTimes = []
articleTextTimes = []

articleKeywordTimes = []

#Get links of the articles of Elon Musk in Times
for i in range(1, nb_page):
    url = "https://time.com/search/?q=elon+musk&page="
    header = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"

    res = requests.get(url+str(i), headers={'User-agent': header})
    soup = BeautifulSoup(res.text, 'html.parser')
    articleList = soup.find_all(attrs={'class': "headline heading-content-tiny margin-8-bottom media-heading"})

    for link in articleList:
        articleLinkTimes.append(str(link.a).split('"')[1])
        articleTitleTimes.append(str(link.a).split('>')[1].split('<')[0])

#function to remove the tags
def remove_tags(tags, text):
    for items in tags:
        text = text.replace(items, "")
    return text

#Use the links getted to scrap the data
for i in range(0, len(articleLinkTimes)):
    #get html
    res = requests.get(articleLinkTimes[i])
    soup = BeautifulSoup(res.text, 'html.parser')
    #find update time
    dateContext = soup.findAll(attrs={"timestamp published-date padding-12-left"})
    articleContext = soup.findAll('p')
    #combine text
    article = ' '.join([str(item) for item in articleContext])
    date = ' '.join([str(item) for item in dateContext])
    #find all tags of text
    tags_date = list(dict.fromkeys(re.findall('<.+?>', str(date))))
    tags_article = list(dict.fromkeys(re.findall('<.+?>', str(articleContext))))
    #remove tags
    articleDateTimes.append(remove_tags(tags_date, date))
    articleTextTimes.append(remove_tags(tags_article, article))

#store data into a dataframe
timeNews = pd.DataFrame({'url': articleLinkTimes, 'title': articleTitleTimes, 'date': articleDateTimes, 'text': articleTextTimes})


timeNews.to_csv("TimesNewsElonMusk1.csv", sep=',', encoding='utf-8')


#Make one DataFrame for the press data
dFBbc = pd.read_csv("BbcElonMusk1.csv")
dFTimes = pd.read_csv("TimesNewsElonMusk1.csv")

dFTimes.insert(0, "media", ['times']*dFTimes.shape[0])
del dFTimes['Unnamed: 0']
del dFBbc['Unnamed: 0']

dFPressMusk = pd.concat([dFBbc,dFTimes], ignore_index=True)

dFPressMusk.to_csv("Press3.csv")


#3. Twitter


#pip install twython
#pip install advertools


pd.set_option('display.max_colwidth', 60)
pd.set_option('display.max.columns', None)  

# parametres de co: 
auth_params = {
    'app_key': 'QhSWQ2MV7wOyy2RtLleKZlEbv',
    'app_secret': 'VDVWCIXI7LELAHplTAunMgOqHbLWBmTf1oqKlz1tn9n2lLTYvT',
    'oauth_token': '1493893476781637637-ZNKEEsdE67I9LxsRkILKyu2EhRaOA4',
    'oauth_token_secret': '0CKzxE63YH094KrCZuwdahSL8ZgvCr0Lwi4jnjHMWMWMr',
}

# twython:
from twython import Twython
twitter = Twython(**auth_params) 


# advertools: 
import advertools as adv
adv.twitter.set_auth_params(**auth_params)


elonmusktweets = adv.twitter.search(q='@elonmusk', count=10000, tweet_mode='extended', lang='en')

elonmusktweets.to_csv('elonmusk.csv', index=False) 

elonmusktweets = pd.read_csv('elonmusk.csv', parse_dates=['tweet_created_at', 'user_created_at'])
# save in a csv

twitterDf = elonmusktweets[["tweet_id", "tweet_created_at", "tweet_full_text", "tweet_entities_hashtags"]]
del twitterDf['Unnamed: 0']

twitterDf.to_csv('twitterElonMusk1.csv')




#Store dataframe into an sql table

    #Create table Press
conn = sqlite3.connect('ElonMuskDb.db')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS Press (Media text, Url text PRIMARY KEY, Title text, Date text, Hour text, Text text, Key_Word text)')
c.execute('CREATE TABLE IF NOT EXISTS Twitter (Tweet_Id text PRIMARY KEY, Date text, Text text, Hashtags text)')
conn.commit()

    #Store press dataframe into Press
dFPressMusk.to_sql('Press', conn, if_exists='replace', index = False)

    #Store Twitter dataframe into Twitter
twitterDf.to_sql('Twitter', conn, if_exists='replace', index = False)