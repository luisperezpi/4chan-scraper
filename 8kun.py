




class Url(object):
    def __init__(self, board_name):
        self._board_name = board_name
        self._protocol = 'https://'

        # 4chan API URL Subdomains
        DOMAIN = {
            'api': self._protocol + 'a.4cdn.org',   # API subdomain
            'boards': self._protocol + 'boards.4chan.org', # HTML subdomain
            'boards_4channel': self._protocol + 'boards.4channel.org', # HTML subdomain of 4channel worksafe, but 4chan.org still redirects
            'file': self._protocol + 'i.4cdn.org',  # file (image) host
            #'file': self._protocol + 'is.4chan.org', # new, slower image host
            'thumbs': self._protocol + 'i.4cdn.org',# thumbs host
            'static': self._protocol + 's.4cdn.org' # static host
        }