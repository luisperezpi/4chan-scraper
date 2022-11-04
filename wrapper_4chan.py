import scrapper_4chan as s4c
import logging
import os
import json
import re
from datetime import datetime

THREADS_DIR = 'threads/'
DATA_DIR = 'data/'
BOARDS_DIR = 'data/boards'
SEARCH_DIR = 'data/searchs'

CATALOG_FILTER = [
    'no',
    'closed',
    'time',
    'name',
    'trip',
    'id',
    'capcode',
    'country',
    'sub',
    'com',
    'tim',
    'filename',
    'ext',
    'filedeleted',
    'replies',
    'images',
    'last_modified',
    'unique_ips',
    'last_replies'
]

THREAD_FILTER = [
    'no',
    'resto',
    'closed'
    'time',
    'name',
    'trip',
    'id',
    'capcode',
    'country',
    'board_flag',
    'flag_name',
    'sub',
    'com',
    'tim',
    'filename',
    'ext',
    'filedeleted',
    'replies',
    'images',
    'last_modified',
    'unique_ips',
    'archived',
    'archived_on'
]

POLITICAL_BOARDS = [
    'pol',
    'bant',
    'biz',
    'lgbt',
    'news',
    'k',
    'int',
    'his',
]

def configure_logger(boardname, board_dir):
    """ Configuración de logger por boardname """
    logger = logging.getLogger(boardname)
    logger.setLevel(logging.INFO)
    info_handler = logging.FileHandler(os.path.join(board_dir, f'info.log'))
    info_handler.setLevel(logging.INFO)
    format = logging.Formatter('[%(asctime)s]:[%(levelname)s] %(name)s - %(message)s')
    info_handler.setFormatter(format)

    error_handler = logging.FileHandler(os.path.join(board_dir, f'error.log'))
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(format)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    return logger

def full_update_board(boardname, board_dir="", catalog_f='catalog.json', logger=None):
    if board_dir == "":
        board_dir = f'{boardname}/'
    board_dir = os.path.join(BOARDS_DIR, board_dir)
    threads_dir = os.path.join(board_dir, THREADS_DIR)
    if not os.path.exists(board_dir):
        os.mkdir(board_dir)
    if not os.path.exists(threads_dir):
        os.mkdir(threads_dir)

    if not logger:
        logger = configure_logger(boardname, board_dir)
    try:
        catalog = s4c.get_catalog(boardname, refresh=True)
        logger.info(f'Scrapping {boardname} board...')
        total = len(list(catalog.keys()))
        logger.info(f'>>>>Found {total} threads on catalog...')
        catalog_f = os.path.join(board_dir, 'catalog.json')
        if os.path.exists(catalog_f):
            with open(catalog_f, 'r') as file:
                catalog_historic = json.load(file)
        else:
            catalog_historic={}


        i=0
        for thread_no, value in catalog.items():
            i+=1
            if str(thread_no) in catalog_historic:
                if value['last_modified'] <= catalog_historic[str(thread_no)]['last_downloaded']:
                    logger.info(f'>>Thread {thread_no} not modified since last download. [{i}/{total}]')
                    continue
            try:
                thread = s4c.get_thread(boardname, thread_no, refresh=True)
                list_posts = []
                for post in thread:
                    list_posts.append({key: post[key] for key in post if key in THREAD_FILTER})
                with open(os.path.join(threads_dir, f'{thread_no}.json'), 'w') as file:
                    json.dump(list_posts, file)
                dict_thread = { key: value[key]  for key in value if key in CATALOG_FILTER}
                dict_thread['last_downloaded'] = dict_thread['last_modified']
                catalog_historic[thread_no] = dict_thread
                logger.info(f'>>Thread {thread_no} downloaded. [{i}/{total}]')
                logger.info(f'>>>>Found {len(list_posts)} posts.')
            except Exception as e:
                logger.exception(f'Error tomando información del thread {thread_no} en board {boardname}.')
                break
        
        with open(os.path.join(board_dir, 'catalog.json'), 'w') as file:
            json.dump(catalog_historic, file)
            logger.info(f'>>Updated historic catalog with new information. ({file.name})')
    except Exception as e:
        logger.exception(f'Error tomando catalog del board {boardname}.')
        

def _quick_search_thread(pattern, thread_dict):
    search_in = ""
    if 'sub' in thread_dict:
        search_in = search_in + thread_dict['sub'] + "\n"
    if 'com' in thread_dict:
        search_in = search_in + thread_dict['com'] + "\n"
    if 'last_replies' in thread_dict:
        for rep in thread_dict['last_replies']:
            if 'com' in thread_dict:
                search_in = search_in + thread_dict['com'] + "\n"
    return re.search(pattern.lower(), search_in.lower())


def search_keyword_board(boardname, pattern, board_dir="", catalog_f='catalog.json', logger=None):
    if board_dir == "":
        board_dir = f'{boardname}/'
    board_dir = os.path.join(BOARDS_DIR, board_dir)
    threads_dir = os.path.join(board_dir, THREADS_DIR)
    if not os.path.exists(board_dir):
        os.mkdir(board_dir)
    if not os.path.exists(threads_dir):
        os.mkdir(threads_dir)

    if not logger:
        logger = configure_logger(boardname, board_dir)
    try:
        catalog = s4c.get_catalog(boardname, refresh=True)
        logger.info(f'Scrapping {boardname} board...')
        total = len(list(catalog.keys()))
        logger.info(f'>>>>Found {total} threads on catalog...')
        catalog_f = os.path.join(board_dir, 'catalog.json')
        if os.path.exists(catalog_f):
            with open(catalog_f, 'r') as file:
                catalog_historic = json.load(file)
        else:
            catalog_historic={}

        list_found_threads = []

        i=0
        for thread_no, value in catalog.items():
            i+=1
            if str(thread_no) in catalog_historic:
                if value['last_modified'] <= catalog_historic[str(thread_no)]['last_downloaded']:
                    logger.info(f'>>Thread {thread_no} not modified since last download. [{i}/{total}]')
                    continue

            if not _quick_search_thread(pattern, value):
                continue

            logger.info(f'>>Thread {thread_no} checks the patterns search. [{i}/{total}]')
            list_found_threads.append(thread_no)
            try:
                thread = s4c.get_thread(boardname, thread_no, refresh=True)
                list_posts = []
                for post in thread:
                    list_posts.append({key: post[key] for key in post if key in THREAD_FILTER})
                with open(os.path.join(threads_dir, f'{thread_no}.json'), 'w') as file:
                    json.dump(list_posts, file)
                dict_thread = { key: value[key]  for key in value if key in CATALOG_FILTER}
                dict_thread['last_downloaded'] = dict_thread['last_modified']
                catalog_historic[thread_no] = dict_thread
                logger.info(f'>>Thread {thread_no} downloaded. [{i}/{total}]')
                logger.info(f'>>>>Found {len(list_posts)} posts.')
            except Exception as e:
                logger.exception(f'Error tomando información del thread {thread_no} en board {boardname}.')
                break
        
        with open(os.path.join(board_dir, 'catalog.json'), 'w') as file:
            json.dump(catalog_historic, file)
            logger.info(f'>>Updated historic catalog with new information. ({file.name})')
        return list_found_threads
    except Exception as e:
        logger.exception(f'Error tomando catalog del board {boardname}.')

        
    
def search_keyword_4chan(pattern, boardname_list=[]):
    if len(boardname_list)==0:
        boardname_list = s4c.get_all_boards_name()
    logger = configure_logger('main', DATA_DIR)
    logger.info(f'Found {len(boardname_list)} boards...')
    search_dict = {}
    now = datetime.now()
    now_str = now.strftime("%d-%m-%Y_%H:%M:%S")
    for boardname in boardname_list:
        list_found_threads = search_keyword_board(boardname, pattern, logger=logger)
        logger.info(f'>>Found {len(list_found_threads)} matching threads in board {boardname}')
        search_dict[boardname] = list_found_threads
    with open(os.path.join(SEARCH_DIR, f'search_{pattern}_{now_str}.json'), 'w') as file:
        json.dump(search_dict, file)



if __name__ == '__main__':
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    if not os.path.exists(SEARCH_DIR):
        os.mkdir(SEARCH_DIR)
    if not os.path.exists(BOARDS_DIR):
        os.mkdir(BOARDS_DIR)
    search_keyword_4chan("russia|nafo|nato|ukrain", boardname_list=POLITICAL_BOARDS)
