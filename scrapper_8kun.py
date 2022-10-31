import requests
import time

_metadata = {}

PROTOCOL = 'https://'

BOARD_KEY = 'uri'

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

#
# TODO: Ahora mismo cada llamada de descarga tiene asociado un sleep 1 sec
# La api de 4chan solo permite una petición por segundo. 
# Esta puesto asi por ahora para evitar baneo pero se tiene que paralelizar con proxies
#

def _fetch_boards_metadata():
    """ Descarga y guarda la información sobre los boards existentes en 4chan  
    
    REF: https://github.com/4chan/4chan-API/blob/master/pages/Boards.md
    """
    if not 'boards' in _metadata:
        _metadata['boards'] = {}

    dir=TEMPLATE['api']['boards']
    resp = requests.get(dir)
    resp.raise_for_status()
    data = {
        entry[BOARD_KEY]:entry for entry in resp.json()['boards']
    }
    _metadata['boards'].update(data)
    time.sleep(1)


def get_all_boards_name(refresh=False):
    """ Devuelve una lista de nombres con los boards existentes en 4chan 
    
    
    refresh: bool, default = True
        Recargar la información al llamar este método
    
    """
    if refresh == True:
        _fetch_boards_metadata()
    try:
        data = list(_metadata['boards'].keys())
    except KeyError:
        _fetch_boards_metadata()
        data = list(_metadata['boards'].keys())
    return data

def get_all_boards_dict(refresh=False):
    """ Devuelve un dict con los boards existentes en 4chan 
        y su informacion pertinente   

    REF: https://github.com/4chan/4chan-API/blob/master/pages/Boards.md 
    
    refresh: bool, default = True
        Recargar la información al llamar este método
    
    """
    if refresh == True or not _metadata:
        _fetch_boards_metadata()
    data = _metadata['boards']
    return data

def _fetch_catalog_metadata(
    boardname
):
    """ Descarga y guarda la información de un board
        haciendo uso del catalog (mas completo que threadlist)
    
    REF: https://github.com/4chan/4chan-API/blob/master/pages/Catalog.md
    """
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

def get_catalog(boardname, page=0, refresh=False, as_dict=True):
    """ Devuelve diccionario o lista con la informacion encontrada en el catalogo de un board   

    REF: https://github.com/4chan/4chan-API/blob/master/pages/Catalog.md 

    boardname: str
        Nombre del board a buscar
    
    refresh: bool, default = True
        Recargar la información al llamar este método
    
    page: int, default = 0
        Pagina de la que sacar threads. Si es 0 se devuelven todos
    
    as_dict: bool, default = True
        Devolver la información como lista de threads o diccionario con el thread_no como key
    
    """
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

    if as_dict==True:
        dict = {}
        for thread in data:
            dict[thread['no']] = thread
        data = dict

    return data

def _fetch_threadlist_metadata(
    boardname
):
    """ Descarga y guarda la información de un board
        haciendo uso del threadlist
    
    REF: https://github.com/4chan/4chan-API/blob/master/pages/Threadlist.md
    """
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

def get_threadlist(boardname, page=0, refresh=False, as_dict=True):
    """ Devuelve diccionario o lista con la informacion encontrada en el catalogo de un board   

    REF: https://github.com/4chan/4chan-API/blob/master/pages/Catalog.md 

    boardname: str
        Nombre del board a buscar
    
    refresh: bool, default = True
        Recargar la información al llamar este método
    
    page: int, default = 0
        Pagina de la que sacar threads. Si es 0 se devuelven todos
    
    as_dict: bool, default = True
        Devolver la información como lista de threads o diccionario con el thread_no como key
    
    """
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

    if as_dict==True:
        dict = {}
        for thread in data:
            dict[thread['no']] = thread
        data = dict

    return data

def _fetch_thread_metadata(
    boardname,
    thread_no
):
    """ Descarga y guarda la información de un thread
    
    REF: https://github.com/4chan/4chan-API/blob/master/pages/Threads.md
    """
    dir=TEMPLATE['api']['thread'].format(
        board=boardname,
        thread_no=thread_no
    )
    if not boardname in _metadata:
        _metadata[boardname] = {}
    if not 'threads' in _metadata[boardname]:
        _metadata[boardname]['threads'] = {}
    
    resp = requests.get(dir)
    resp.raise_for_status()
    data = resp.json()['posts']
    _metadata[boardname]['threads'][thread_no] = data
    time.sleep(1)


def get_thread(
    boardname,
    thread_no,
    refresh=False
):
    """ Devuelve la información de un thread
    
    REF: https://github.com/4chan/4chan-API/blob/master/pages/Threads.md

    boardname: str
        Nombre del board al que pertenece el thread
    
    thread_no: str
        Id del thread a descargar

    refresh: bool, default=False
        Recargar la información al llamar este método
    """
    if refresh == True:
        _fetch_thread_metadata(boardname, thread_no)
    try:
        data = _metadata[boardname]['threads'][thread_no]
    except KeyError:
        _fetch_thread_metadata(boardname, thread_no)
        data = _metadata[boardname]['threads'][thread_no]
    return data

def is_thread_active(
    boardname,
    thread_no
):
    """ Comprueba si un thread esta accesible mediante la api
    
    REF: https://github.com/4chan/4chan-API/blob/master/pages/Threads.md

    boardname: str
        Nombre del board al que pertenece el thread
    
    thread_no: str
        Id del thread a comprobar
    """
    dir=TEMPLATE['api']['thread'].format(
        board=boardname,
        thread_no=thread_no
    )

    return requests.get(dir).ok


def _fetch_archive_metadata(
    boardname
):
    """ Descarga y guarda la lista de threads archivada de un board
        Muchos de estos threads podrian no ser accesibles
    
    REF: https://github.com/4chan/4chan-API/blob/master/pages/Archive.md
    """
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
    """ Devuelve la lista de threads archivada de un board
        Muchos de estos threads podrian no ser accesibles
    
    REF: https://github.com/4chan/4chan-API/blob/master/pages/Archive.md
    
    refresh: bool, default = True
        Recargar la información al llamar este método
    """
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
    """ Devuelve la url en la que se aloja un archivo
    
    REF: https://github.com/4chan/4chan-API/blob/master/pages/User_images_and_static_content.md
    
    boardname: str
        Nombre del board en el que se encontro la imagen

    file_tim: str
        Time en el que se subio la imagen
        (Se puede encontrar en la informacion del thread donde aparecio)

    file_extension: str, default=.jpg
        Extension del archivo
    
    thumb: bool, default =False
        General url para obtener la miniatura de una imagen
    """
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
    """ Devuelve la url en la que se aloja un a imagen static de 4chan
    
    REF: https://github.com/4chan/4chan-API/blob/master/pages/User_images_and_static_content.md
    
    item: str
        Indica el static a devolver
    """
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
    
