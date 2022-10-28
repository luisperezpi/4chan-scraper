
from concurrent.futures import thread
from distutils import extension
import requests
import time

_metadata = {}

PROTOCOL = 'https://'

DOMAIN = {
    'api': PROTOCOL + '8kun.top',   # API subdomain
    'boards': PROTOCOL + 'boards.4chan.org', # HTML subdomain
    'boards_4channel': PROTOCOL + 'boards.4channel.org', # HTML subdomain of 4channel worksafe, but 4chan.org still redirects
    'file': PROTOCOL + 'i.4cdn.org',  # file (image) host
    #'file': PROTOCOL + 'is.4chan.org', # new, slower image host
    'thumbs': PROTOCOL + 'i.4cdn.org',# thumbs host
    'static': PROTOCOL + 's.4cdn.org' # static host
}


# TODO: archive no funciona aun
# 4chan API URL Templates
TEMPLATE = {
    'api': {  # URL structure templates
        'boards': DOMAIN['api'] + '/boards.json',
        'catalog': DOMAIN['api'] + '/{board}/catalog.json',
        'threadlist': DOMAIN['api'] + '/{board}/threads.json',
        'thread': DOMAIN['api'] + '/{board}/res/{thread_id}.json',
        'archive': DOMAIN['api'] + '/{board}/archive.json'
    },
    'http': { # Standard HTTP viewing URLs
        'board': DOMAIN['boards'] + '/{board}/{page}',
        'thread': DOMAIN['boards'] + '/{board}/thread/{thread_id}'
    },
    'data': {
        'file': DOMAIN['file'] + '/{board}/{tim}{ext}',
        'thumbs': DOMAIN['thumbs'] + '/{board}/{tim}s.jpg',
        'static': DOMAIN['static'] + '/image/{item}'
    }
}

def _fetch_boards_metadata():
    if not 'boards' in _metadata:
        _metadata['boards'] = {}

    dir=TEMPLATE['api']['boards']
    resp = requests.get(dir)
    resp.raise_for_status()
    data = {
        entry['uri']:entry for entry in resp.json()
    }
    _metadata['boards'].update(data)
    time.sleep(1)

def get_all_boards_name(refresh=False):
    if refresh == True:
        _fetch_boards_metadata()
    try:
        data = list(_metadata['boards'].keys())
    except KeyError:
        _fetch_boards_metadata()
        data = list(_metadata['boards'].keys())
    return data

def get_all_boards_dict(refresh=False):
    if refresh == True or not _metadata:
        _fetch_boards_metadata()
    data = _metadata['boards']
    return data

def _fetch_catalog_metadata(
    boardname
):
    dir=TEMPLATE['api']['catalog'].format(
        board=boardname
    )
    if not boardname in _metadata:
        _metadata[boardname] = {}
    
    resp = requests.get(dir)
    resp.raise_for_status()
    data = resp.json()
    _metadata[boardname]['catalog']= data
    time.sleep(1)

def get_catalog(boardname, page=0, refresh=False):
    if refresh == True: 
        _fetch_catalog_metadata(boardname)
    while True:
        try:
            if page != 0:
                data = _metadata[boardname]['catalog'][page-1]
            else:
                data = []
                for page in _metadata[boardname]['catalog']:
                    data = data + page['threads']   
        except KeyError:
            _fetch_catalog_metadata(boardname)
            continue
        break
    return data

def _fetch_threadlist_metadata(
    boardname
):
    dir=TEMPLATE['api']['threadlist'].format(
        board=boardname
    )
    if not boardname in _metadata:
        _metadata[boardname] = {}
    
    resp = requests.get(dir)
    resp.raise_for_status()
    data = resp.json()
    _metadata[boardname]['threadlist']= data
    time.sleep(1)

def get_threadlist(boardname, page=0, refresh=False):
    if refresh == True: 
        _fetch_threadlist_metadata(boardname)
    while True:
        try:
            if page != 0:
                data = _metadata[boardname]['threadlist'][page-1]
            else:
                data = []
                for page in _metadata[boardname]['threadlist']:
                    data = data + page['threads']   
        except KeyError:
            _fetch_threadlist_metadata(boardname)
            continue
        break
    return data

def _fetch_thread_metadata(
    boardname,
    thread_id
):
    dir=TEMPLATE['api']['thread'].format(
        board=boardname,
        thread_id=thread_id
    )
    if not boardname in _metadata:
        _metadata[boardname] = {}
    if not 'threads' in _metadata[boardname]:
        _metadata[boardname]['threads'] = {}
    
    resp = requests.get(dir)
    resp.raise_for_status()
    data = resp.json()['posts']
    _metadata[boardname]['threads'][thread_id] = data
    time.sleep(1)


def get_thread(
    boardname,
    thread_id,
    refresh=False
):
    if refresh == True:
        _fetch_thread_metadata(boardname, thread_id)
    try:
        data = _metadata[boardname]['threads'][thread_id]
    except KeyError:
        _fetch_thread_metadata(boardname, thread_id)
        data = _metadata[boardname]['threads'][thread_id]
    return data

def is_thread_active(
    boardname,
    thread_id
):
    dir=TEMPLATE['api']['thread'].format(
        board=boardname,
        thread_id=thread_id
    )

    return requests.get(dir).ok


def _fetch_archive_metadata(
    boardname
):
    dir=TEMPLATE['api']['archive'].format(
        board=boardname
    )
    if not boardname in _metadata:
        _metadata[boardname] = {}
    
    resp = requests.get(dir)
    resp.raise_for_status()
    data = resp.json()
    _metadata[boardname]['archive']= data
    time.sleep(1)
    


def get_archive(
    boardname,
    refresh=False
):
    if refresh == True:
        _fetch_archive_metadata(boardname)
    try:
        data = _metadata[boardname]['archive']
    except KeyError:
        _fetch_archive_metadata(boardname)
        data = _metadata[boardname]['archive']
    return data

def get_file_url(
    boardname,
    file_tim,
    file_extension=".jpg",
    thumb=False
):
    if thumb:
        dir=TEMPLATE['data']['thumbs'].format(
            board=boardname,
            tim=file_tim
        )
    else:
        dir=TEMPLATE['data']['file'].format(
            board=boardname,
            tim=file_tim,
            ext=file_extension
        )
    return dir

def get_static_url(
    item
):
    dir=TEMPLATE['data']['static'].format(
        item=item
    )
    return dir


def refresh_board(
    boardname
):
    list_of_failed_threads_cat = []
    _fetch_catalog_metadata(boardname)
    _fetch_archive_metadata(boardname)
    for page in _metadata[boardname]['catalog']:   
        for thread in page['threads']:
            if is_thread_active(boardname, thread['no']):
                _fetch_thread_metadata(boardname, thread['no']) 
            else:
                list_of_failed_threads_cat.append(thread['no'])

    
    for thread in  _metadata[boardname]['archive']:
        if is_thread_active(boardname, thread):
            _fetch_thread_metadata(boardname, thread) 
    return list_of_failed_threads_cat



def refresh_boards():
    failed_dict = {}
    _fetch_boards_metadata()
    for boardname in _metadata['boards'].keys():
        failed_dict[boardname]=refresh_board(boardname)
    
