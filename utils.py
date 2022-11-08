import string
import nltk
import re
import emoji
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

"""Module that includes methods to tag specific words in tweets.

In particular the module allows to tag:
    - url > URL
    - userref > REF
    - hashtags > TAG
    - dates > DAT
    - times > TIM
    - number > NUM

Most of the code is coppied from:
https://github.com/theocjr/social-media-forensics/blob/master/
microblog_authorship_attribution/dataset_pre_processing/
tagging_irrelevant_data.py
"""

import re


def tag_url(text):
    # source: http://stackoverflow.com/questions/6883049/regex-to-find-urls-in-string-in-python
    # test: import re; re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+' , u'URL', 'ahttp:/www.uol.com.br ahttp://www.uol.com.br https://255.255.255.255/teste http://www.255.1.com/outroteste a a a ')
    #return re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+' , u'URL', text)

    # Thiago Cavalcante's approach
    return re.sub('((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)', u'URL', text)


def tag_userref(text):
    # rational: a username must start with a '@' and have unlimited occurences of letters, numbers and underscores.
    # test: import re; re.sub('(?<!\S)@[0-9a-zA-Z_]{1,}(?![0-9a-zA-Z_])', u'REF', '@user @us3r @1user @1234567890123456 @_0334 @vser @_ @1 @faeeeec-cas caece ce ce asdcc@notuser ewdede-@dqwec email@some.com.br @ @aaa')
    #return re.sub('(?<!\S)@[0-9a-zA-Z_]{1,}(?![0-9a-zA-Z_])', u'REF', text)

    # Thiago Cavalcante's approach
    return re.sub('@[^\s]+', u'REF', text)


def tag_hashtag(text):
    # rationale: https://support.twitter.com/articles/49309
    # test: import re; re.sub('(?<!\S)(#[0-9a-zA-Z_-]+)(?![0-9a-zA-Z_-])', u'TAG', '#anotherhash #123 #a123 a not#hash #[]aaa #avbjd')
    #return re.sub('(?<!\S)(#[0-9a-zA-Z_-]+)(?![0-9a-zA-Z_-])', u'TAG', text)

    # Thiago Cavalcante's approach
    return re.sub('#[a-zA-Z]+', u'TAG', text)


def tag_date(text):
    # rationale: a date is a two or three blocks of digits separated by a slash.
    # test: import re; re.sub(('(?<!\S)('
    #                                       '[0-3]?[0-9]\s?[/-]\s?[0-3]?[0-9]\s?[/-]\s?[0-9]{1,4}|'     # DD/MM/YYYY or MM/DD/YYYY
    #                                       '[0-1]?[0-9]\s?[/-]\s?[0-9]{1,4}|'                          # MM/YYYY
    #                                       '[0-9]{1,4}\s?[/-]\s?[0-1]?[0-9]|'                          # YYYY/MM
    #                                       '[0-3]?[0-9]\s?[/-]\s?[0-3]?[0-9]'                          # DD/MM or MM/DD
    #                       '            )(?![0-9a-zA-Z])'
    #                           ), u'DAT', '23/12/1977 12 - 23- 2014 25-10 12 / 23 09/2013 1999 - 02 90/12 a12/94 12/31. 12/31a 12-31')
    #return re.sub(('(?<!\S)('
    #                            '[0-3]?[0-9]\s?[/-]\s?[0-3]?[0-9]\s?[/-]\s?[0-9]{1,4}|'     # DD/MM/YYYY or MM/DD/YYYY
    #                            '[0-1]?[0-9]\s?[/-]\s?[0-9]{1,4}|'                          # MM/YYYY
    #                            '[0-9]{1,4}\s?[/-]\s?[0-1]?[0-9]|'                          # YYYY/MM
    #                            '[0-3]?[0-9]\s?[/-]\s?[0-3]?[0-9]'                          # DD/MM or MM/DD
    #                       ')(?![0-9a-zA-Z])'
    #               ), u'DAT', text)

    # Thiago Cavalcante's approach
    return re.sub('[0-9]?[0-9][-/][0-9]?[0-9]([-/][0-9][0-9][0-9][0-9])?', u'DAT', text)


def tag_time(text):
    # rationale: a time is one or two digits followed by a colon and one or two more digits followed by an optional seconds block. An optional AM/PM suffix can also occur.
    # test: import re; re.sub('(?<!\S)([0-2]?[0-9]:[0-5]?[0-9](:[0-5]?[0-9])?\s?([A|P]M)?)(?![0-9a-zA-Z])', u'TIM', '00:00 AM 1:01PM 2:2 pm 01:02:03 Am 01:02. 03:12! 03:14a bbb 60:60 3:40am', flags=re.IGNORECASE)
    #return re.sub('(?<!\S)([0-2]?[0-9]:[0-5]?[0-9](:[0-5]?[0-9])?\s?([A|P]M)?)(?![0-9a-zA-Z])', u'TIM', text, flags=re.IGNORECASE)

    # Thiago Cavalcante's approach
    return re.sub('[0-9]?[0-9]:[0-9]?[0-9](:[0-9]?[0-9])?', u'TIM', text)


def tag_number(text):
    # rationale: a number is a group of consecutive digits, comma and points, prefixed by a optional plus/minus. Obs: expected very few false positives
    # test: import re; re.sub('(?<!\S)([+-]?[0-9.,]*[0-9])(?![0-9a-zA-Z+-])', u'NUM', '98.786    123 123.1 345,2 32, 56. .92 ,34 100,000.00 +11,3 -10 10? 10! 1,1..2 1-1 1+1 dadcd12  89hjgj tt.bt.65bnnn 98,3')
    #return re.sub('(?<!\S)([+-]?[0-9.,]*[0-9])(?![0-9a-zA-Z+-])', u'NUM', text)

    # rationale: a number is a group of three possibilities: 1) a leading digits followed by point/comma and optional decimal digits; 2) leading comma/point followed by digits; 3) numbers without comma/point
    # test: import re; re.sub('(?<!\S)([0-9]+[,.][0-9]*|[,.][0-9]+|[0-9]+)(?=\s|$)', u'NUM', '98.786    123 123.1 345,2 32, 56. .92 ,34 dadcd12  89hjgj tt.bt.65bnnn 98,3')
    # return re.sub('(?<!\S)([0-9]+[,.][0-9]*|[,.][0-9]+|[0-9]+)(?=\s|$)', u'NUM', text)

    # Thiago Cavalcante's approach
    return re.sub('[0-9]+', u'NUM', text)


def tag(
    tweet,
    url=True,
    userref=True,
    hashtag=True,
    date=True,
    time=True,
    number=True
):

    if url:
        tweet = tag_url(tweet)
    if userref:
        tweet = tag_userref(tweet)
    if hashtag:
        tweet = tag_hashtag(tweet)
    if date:
        tweet = tag_date(tweet)
    if time:
        tweet = tag_time(tweet)
    if number:
        tweet = tag_number(tweet)

    return tweet

def clean_text(text, lang="en", clean_stopwords=True, to_steam=True):
    #lowercase
    text = text.lower()
    
    #emoji clean
    text = emoji.replace_emoji(text, replace="")
    
    # Remove punctuation
    table = str.maketrans('', '', string.punctuation + "“" + "”" + "¿" + "¡" + "–" + "‘" + "’")
    stripped_text = text.translate(table)
    
    # Split in words (and remove tags from data_tagger.py)
    words = [w for w in stripped_text.split() if w not in ["rt", "ref", "num", "dat", "url", "tag", "tim"]]
    
    # SELECT BY LANGUAGE
    if lang == "en":
        black_list_stopwords = []#["over", "than", "too", "very", "more", "most", "same", "very", "nor", "not"]
        stopwords_list = stopwords.words('english')
        stemmer = SnowballStemmer("english")
    elif lang == "es":
        black_list_stopwords = ["antes", "con", "contra", "desde", "durante", "mucho", "muchos", "muy", "más", "ni", "no", "sin", "tuyos", "tuyas", "tú", "yo", "él"]
        stopwords_list = stopwords.words('spanish')
        stemmer = SnowballStemmer("spanish")
    else:
        black_list_stopwords = []
        stopwords_list = []
        
    # Stopwords
    if clean_stopwords:
        stop_words = [s for s in set(stopwords_list) if s not in black_list_stopwords]
        words = [w for w in words if not w in stop_words]            
    
    # Stemming -> reduce words to its root
    # Some 'pandemic invented' words are better to avoid them from stemming
    if to_steam:
        black_list = ["covid"]
        words = [stemmer.stem(w) if not any(ban in w for ban in black_list) else w for w in words]
    
    # Finally, the text is joined by whitespaces (we needed like this for ncd method)
    cleaned_text = " ".join(words)
    
    return cleaned_text


def get_bog_to_keep(lang="en"):
    
    if lang == "en":
        # Bag of worlds of the content we want to keep
        WHITE_LIST_BOG = [
            "covid", "vaccin", "vaccine", "ivermectin",
            "experiment", "dose", "flu",
            "muzzle", "mask", "wakeup", "infection",
            "pfizer", "pandemic", "nwo", "pox", "myocarditis", "transmission", "virus"] #COVID Related
        
    elif lang == "es":
    # Bag of worlds of the content we want to keep
        WHITE_LIST_BOG = [
            "covid", "vacun", "vaccine",
            "experiment", "dosis", "gripe",
            "bozal", "mascarilla", "mividamioxigeno",
            "baldosasamarillas", "pandemia", "plandemia", "ganado", "inocula", "contagi", "virus"] #COVID Related
    
    else:
        WHITE_LIST_BOG = []

    reg_bag_of_worlds = "|".join(WHITE_LIST_BOG) #Regex expresion for filter dataset
    
    return reg_bag_of_worlds



def filter_content(df, lang="en"):

    reg_bag_of_worlds = get_bog_to_keep(lang="en")

    df_filtered = df.loc[df["content"].str.contains(reg_bag_of_worlds, case=False)]
    
    return df_filtered