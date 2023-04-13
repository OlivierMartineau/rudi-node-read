from http.client import HTTPSConnection
from urllib.parse import urlsplit

from utils.log import log_e, log_d


def https_download(url):
    (scheme, netloc, path, query, fragment) = urlsplit(url)
    if scheme != 'https':
        raise NotImplementedError('only HTTPS protocol is supported')
    connection = HTTPSConnection(netloc)
    connection.request(method='GET', url=url)
    response = connection.getresponse()
    if response.status != 200:
        log_e('https_download', f'ERR {response.status}', url)
        return None
    else:
        log_d('https_download', f'OK {response.status}', url)
    data = response.read()
    # log_d('https_download', 'data', data)
    connection.close()
    return data


if __name__ == '__main__':
    url = 'https://bacasable.fenix.rudi-univ-rennes1.fr/media/download/b086c7b2-bd6d-401f-86f5-f1f207023bae'
    log_d('https_download', url, https_download(url))
