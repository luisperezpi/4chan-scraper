import os
import json
from bs4 import BeautifulSoup
import re
import datetime

from flair.data import Sentence
from flair.models.sequence_tagger_model import SequenceTagger

THREADS_DIR = 'threads'
DATA_DIR = '/home/luis/data/4chan'
BOARDS_DIR = 'boards'
SEARCH_DIR = 'searchs'
ANALYSIS_DIR = 'analysis'

WANTED_BOARDS = ['pol']


tagger = SequenceTagger.load("ner-fast")

def full_board_texts(boards_list):
    boards_dp = os.path.join(DATA_DIR, BOARDS_DIR)

    for boardname in boards_list:
    
        board_dp = os.path.join(boards_dp, f'{boardname}/')
        thread_dp = os.path.join(board_dp, THREADS_DIR)

        for file in os.listdir(thread_dp):
            with open(os.path.join(thread_dp, file), "r") as f:
                dict_list = json.load(f)
                for th_dict in dict_list:
                    if 'sub' in th_dict:
                        text_list.append(th_dict['sub'])
                    if 'com' in th_dict:
                        text_list.append(th_dict['com'])
    
    text = "\n".join(text_list)

    # Remove quotes signifiers
    text = re.sub("&gt;&gt;\d{8}", "", text)
    text = re.sub("<br><span class=\"quote\">&gt;", "", text)
    text = re.sub("</span><br>", " ", text)
    soup = BeautifulSoup(text,'html.parser')
    return soup.get_text()


def _sort_dict(unsorted_dict):
    for label, value in unsorted_dict.items():
        unsorted_dict[label] = dict(sorted(value.items(), key=lambda item: item[1], reverse=True))
    return unsorted_dict


def ner_text(text):

    sentence = Sentence(text)
    tagger.predict(sentence)

    entities = {}
    for span in sentence.get_spans("ner"):

        if span.tag not in entities:
            entities[span.tag] = {}
        if span.text in entities[span.tag]:
            entities[span.tag][span.text] += 1
        else:
            entities[span.tag][span.text] = 1

    return entities


if __name__ == '__main__':
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    if not os.path.exists(BOARDS_DIR):
        os.mkdir(BOARDS_DIR)
    if not os.path.exists(ANALYSIS_DIR):
        os.mkdir(ANALYSIS_DIR)
    res = ner_text(full_board_texts(WANTED_BOARDS))
    res = _sort_dict(res)


    now = datetime.now()
    now_str = now.strftime("%d-%m-%Y_%H:%M:%S")
    with open(os.path.join(ANALYSIS_DIR, f'analysis_{now_str}.json'), 'w') as file:
        json.dump(res, file, indent=4)