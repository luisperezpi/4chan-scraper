import os
import json
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas as pd
from tqdm import tqdm

from sklearn.feature_extraction.text import CountVectorizer

from flair.data import Sentence
from flair.models.sequence_tagger_model import SequenceTagger

import paramiko

if not os.environ.get('GICSERVER_PW'):
    raise ValueError('GICSERVER_PW env variable not set.')


THREADS_DIR = 'threads'
SSH_DATA_DIR = '/home/luis/data/4chan'
DATA_DIR = "data/4chan"
BOARDS_DIR = 'boards'
SEARCH_DIR = 'searchs'
ANALYSIS_DIR = 'data/4chan/analysis'

WANTED_BOARDS = ['pol']

BATCH_COMMENTS_SIZE = 50

tagger = SequenceTagger.load("ner-fast")

def connect_ssh():
    ssh_client=paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname='gicserver',username='luis',password=os.environ.get('GICSERVER_PW'))
    return ssh_client

def dw_full_board_texts(boards_list, ssh_client):
    boards_dp = os.path.join(SSH_DATA_DIR, BOARDS_DIR)
    text_dict = {}

    for boardname in boards_list:
        text_list = []
        board_dp = os.path.join(boards_dp, f'{boardname}/')
        thread_dp = os.path.join(board_dp, THREADS_DIR)
        ftp_client = ssh_client.open_sftp()
        for file in ftp_client.listdir(thread_dp):
            text_dict[boardname]=[]
            f = ftp_client.open(os.path.join(thread_dp, file), "r")
            dict_list = json.load(f)
            for th_dict in dict_list:
                if 'sub' in th_dict:
                    text_list.append(th_dict['sub'])
                if 'com' in th_dict:
                    text_list.append(th_dict['com'])
            f.close()
        ftp_client.close()
        text_dict[boardname] = text_list

    with open(os.path.join(DATA_DIR, 'fulltext.json'), 'w') as file:
        json.dump(text_dict, file)
    return text_dict

def read_full_board_texts(boards_list, ssh_client):
    if 'fulltext.json' in os.listdir(DATA_DIR):
        with open(os.path.join(DATA_DIR, 'fulltext.json'), 'r') as file:
            text_dict = json.load(file)
        return text_dict
    else:
        return dw_full_board_texts(boards_list, ssh_client)



def clean_text(text_list):
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


def ner_text(text, entities={}):

    sentence = Sentence(text)
    tagger.predict(sentence)

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
    ssh_client = connect_ssh()
    text_dict = read_full_board_texts(WANTED_BOARDS,ssh_client)
    entities = {}
    for item, value in text_dict.items():
        for i in tqdm(range(0, len(value), BATCH_COMMENTS_SIZE)):
            chunks = value[i:i+BATCH_COMMENTS_SIZE] 
            entities = ner_text(clean_text(chunks), entities=entities)
    entities = _sort_dict(entities)
    now = datetime.now()
    now_str = now.strftime("%d-%m-%Y_%H:%M:%S")
    with open(os.path.join(ANALYSIS_DIR, f'analysis_{now_str}.json'), 'w') as file:
        json.dump(entities, file, indent=4)