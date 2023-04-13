from conf_read.conf_reader import IniReader
from utils.log import log_d
from utils.serializable import Serializable

''' -----------------------------------------------------------------------------------------------
    Constants
    ------------------------------------------------------------------------------------------------
'''
# Default "Jwt forge" config file
CONF_CONNECTOR_DEFAULT_PATH = '../0-ini/connectors_conf.ini'

# Default credentials file
CONF_RUDI_NODE_CREDS = '../0-creds/rudi_node_credentials.ini'

# JWT sections parameters
JWT_SECTION = 'JWT_FORGE'
JWT_PARAM_URL = 'jwt_forge_url'
JWt_PARAM_SUB = 'jwt_sub'
JWT_PARAM_CID = 'jwt_client_id'
JWT_PARAM_EXP = 'jwt_duration_s'

# RUDI_NODE section parameters
RUDI_NODE_SECTION = 'RUDI_NODE'
RUDI_NODE_PARAM_URL = 'rudi_node_url'

# Credentials section parameters
MEDIA_CREDS_SECTION = 'RUDI_MEDIA'
MEDIA_CREDS_PARAM_USR = 'media_usr'
MEDIA_CREDS_PARAM_PWD = 'media_pwd'

# DATA_SOURCE section parameters
DATA_SOURCE_SECTION = 'DATA_SOURCE'
DATA_SOURCE_PARAM_URL = 'data_source_url'
DATA_SOURCE_PARAM_TYPE = 'data_source_type'

# REQUEST_HEADER section parameters
HDR_SECTION = 'REQUEST_HEADER'
HDR_PARAM_USR = 'user_agent'

''' -----------------------------------------------------------------------------------------------
    Class ConnectorConfReader
    ------------------------------------------------------------------------------------------------
'''


class ConnectorConfReader(Serializable):
    _defaults = None

    def __init__(self, conf_file_path):
        # Conf file
        ini_conf = IniReader(conf_file_path)

        # Rudi Node parameters
        self.rudi_node_url = ini_conf.get(RUDI_NODE_SECTION, RUDI_NODE_PARAM_URL, 'a URL is expected')

        self.hdr_user_agent = ini_conf.get(HDR_SECTION, HDR_PARAM_USR,
                                           'an id is required to identify the request sender in headers')

    @staticmethod
    def load(conf_file_path: str = CONF_CONNECTOR_DEFAULT_PATH):
        return ConnectorConfReader(conf_file_path)

    @staticmethod
    def get_defaults():
        if ConnectorConfReader._defaults is None:
            ConnectorConfReader._defaults = ConnectorConfReader(CONF_CONNECTOR_DEFAULT_PATH
                                                                )
        return ConnectorConfReader._defaults


if __name__ == '__main__':
    connections_conf = ConnectorConfReader.get_defaults()
    log_d('ConnectorConfReader', 'rudi_node_url', connections_conf.rudi_node_url)
