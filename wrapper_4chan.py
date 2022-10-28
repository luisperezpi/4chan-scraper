import scrapper_4chan as s4c
import logging
import os
import json


THREADS_DIR = 'threads/'
DATA_DIR = 'data/'

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


def configure_logger(boardname, board_dir):
    logger = logging.getLogger(boardname)
    info_handler = logging.FileHandler(os.path.join(board_dir, f'{boardname}.log'))
    info_handler.setLevel(logging.INFO)
    info_handler.setLevel(logging.INFO)
    info_format = logging.Formatter('[%(asctime)s]:[%(levelname)s] %(name)s - %(message)s')
    info_handler.setFormatter(info_format)
    logger.addHandler(info_handler)
    return logger

def full_update_board(boardname, board_dir="", catalog_f='catalog.json'):
    if board_dir == "":
        board_dir = f'{boardname}/'
    board_dir = os.path.join(DATA_DIR, board_dir)
    threads_dir = os.path.join(board_dir, THREADS_DIR)
    if not os.path.exists(board_dir):
        os.mkdir(board_dir)
    if not os.path.exists(threads_dir):
        os.mkdir(threads_dir)

    logger = configure_logger(boardname, board_dir)
    try:
        catalog = s4c.get_catalog(boardname, refresh=True)
        logging.info(f'Scrapping {boardname} board...')
        logging.info(f'>>>>Found {len(list(catalog.keys()))} threads on catalog...')
        with open(os.paht.join(board_dir, 'catalog.json'), 'r') as file:
            catalog_historic = json.load(file)

        update_dict = {}
        for thread_no in catalog.keys():
            if thread_no in catalog_historic.keys():
                if catalog[thread_no]['last_modified'] <= catalog_historic[thread_no]['last_modified']:
                    logging.info(f'>>Thread {thread_no} not modified since last download.')
                    continue
            try:
                thread = s4c.get_thread(boardname, thread_no, refresh=True)
                list_posts = []
                for post in thread['posts']:
                    list_posts.append({key: post[key] for key in post if key in THREAD_FILTER})
                with open(os.paht.join(threads_dir, f'{thread_no}.json'), 'w') as file:
                    json.dump(list_posts, file)
                dict_thread = { key: catalog[thread_no][key]  for key in catalog[thread_no] if key in CATALOG_FILTER}
                update_dict[thread_no] = dict_thread
                logging.info(f'>>Thread {thread_no} downloaded.')
                logging.info(f'>>>>Found {len(list_posts)} posts.')
            except Exception as e:
                logger.exception(f'Error tomando información del thread {thread_no} en board {boardname}.')
                break
                    
        catalog_historic.update(update_dict)
        with open(os.paht.join(board_dir, 'catalog.json'), 'w') as file:
            json.dump(catalog_historic, file)
        logging.info(f'>>Updated historic catalog with new information.')
    except Exception as e:
        logger.exception(f'Error tomando catalog del board {boardname}.')
        



    


    