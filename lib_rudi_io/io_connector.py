from http.client import HTTPSConnection, HTTPConnection
from json import dumps, loads, JSONDecodeError
from typing import Literal, Final, get_args
from urllib.parse import urlsplit

from utils.err import HttpError, LiteralUnexpectedValueException
from utils.log import log_d_if, log_e, log_d
from utils.serializable import Serializable
from utils.string_utils import slash_join

HttpRequestMethod: Final = Literal['GET', 'PUT', 'DEL', 'POST']
http_request_methods = get_args(HttpRequestMethod)


class Connector(Serializable):
    _default_connector = None

    def __init__(self, server_url: str):
        (scheme, netloc, path, query, fragment) = urlsplit(server_url)
        if scheme != 'http' and scheme != 'https':
            raise NotImplementedError('only http and https are supported')
        self.scheme = scheme
        self.host = netloc
        self.path = path
        self.base_url = slash_join(f"{self.scheme}://{self.host}", self.path)

        log_d('Connector', 'base_url', self.base_url)

    def full_url(self, url: str = '/'):
        return slash_join(self.base_url, url)

    def full_path(self, url: str = '/'):
        return slash_join('/', self.path, url)

    def request(self,
                url: str = '/',
                req_method: HttpRequestMethod = 'GET',
                body: object = None,
                headers: object = None,
                should_log_response: bool = False) -> (str, object):
        """ Send a http(obj) request
        """
        if self.scheme == 'https':
            connection = HTTPSConnection(self.host)
        else:
            connection = HTTPConnection(self.host)
        if req_method not in http_request_methods:
            raise LiteralUnexpectedValueException('incorrect type for request method', HttpRequestMethod, req_method)

        if not headers:
            headers = {
                'Content-Type': 'text/plain',
                'Accept': 'application/json'
            }
        # log_d(f'{self.__class__.__name__}.request', 'url', url)
        # log_d_if(should_log_response, 'headers', headers)
        if body and type(body) == dict:
            headers['Content-type'] = 'application/json'
            body = dumps(body)

        path_url = self.full_path(url)
        log_d(f'{self.__class__.__name__}.request', 'to', self.full_url(url))
        try:
            connection.request(req_method, path_url, body, headers)
        except ConnectionRefusedError as e:
            log_e(self.__class__.__name__, 'Error on request', req_method,
                  self.full_url(url))
            log_e(self.__class__.__name__, 'ERR', e)
            raise e
        return self.parse_response(connection, url, req_method, headers, body,
                                   should_log_response)

    def parse_response(self,
                       connection: HTTPConnection,
                       url,
                       req_method,
                       headers,
                       body,
                       should_log_response: bool = True):
        """ Basic parsing of the result
        """
        fun = f'{self.__class__.__name__}.parse_response'
        response = connection.getresponse()
        if response.status not in [200, 500, 501] \
                and not (530 <= response.status < 540) \
                and not (400 <= response.status < 500):
            return None

        rdata = response.read()
        try:
            response_data = loads(rdata)
            log_d_if(should_log_response, fun, 'Response is a JSON', response_data)
        except (TypeError, JSONDecodeError) as e:
            response_data = repr(rdata)
            log_d_if(should_log_response, fun, 'Response is not a JSON', response_data)
        connection.close()
        if type(response_data) is str:
            log_d_if(should_log_response, fun, 'Response is a string', response_data)
            if response.status == 200:
                return rdata.decode('utf8')
        if response.status == 200:
            return response_data
        if response.status >= 400:
            log_e(fun, 'Connection error', response_data)
            log_e(fun, 'Request in error', req_method, self.full_url(url))
            raise HttpError(response_data, req_method, self.base_url, url)


if __name__ == '__main__':
    if 'GET' in HttpRequestMethod:
        log_d('Testing Literal', 'GET in HttpRequestMethod', 'OK')
    else:
        log_d('Testing Literal', 'GET in HttpRequestMethod', 'KO')

    connector = Connector('https://data-rudi.aqmo.org/api/v1')
    data = connector.request(url='resources?limit=1')
    print(data)
