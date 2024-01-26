from rudi_node_read.connectors.io_connector import Connector, STATUS, REDIRECTION
from rudi_node_read.utils.log import log_d, log_e
from rudi_node_read.utils.type_dict import is_dict
from rudi_node_read.utils.type_string import slash_join

REQ_LIMIT = 500


class RudiNodeConnector(Connector):
    def __init__(self, server_url: str, headers_user_agent: str = "RudiNodeConnector"):
        """
        Creates a connector to the API/proxy module of a RUDI Node
        :param server_url: the URL of the RUDI Node
        :param headers_user_agent: (optional) identifies the user launching the request (or at least the module)
        in the request headers, for logging purpose.
        """
        here = "RudiNodeConnector.__init__"

        super().__init__(server_url)

        # log_d("RudiNodeConnector", "attributes", self)
        self.test_rudi_api_connection()
        self._headers = {
            "User-Agent": headers_user_agent,
            "Content-type": "text/plain",
            "Accept": "application/json",
        }

    def get_api(self, url: str):
        """
        Performs an identified GET request through /api/v1 path
        :param url: part of the URL that comes after /api/admin
        :return: a JSON
        """
        return self.request(url=slash_join("api/v1", url), req_method="GET", headers=self._headers)

    def test_rudi_api_connection(self):
        test_path = "api/admin/hash"
        test = self.request(test_path)
        if test is None:
            log_e("RudiNodeConnector", f"!! Node '{self.host}'", "no connection!")
            raise ConnectionError(f"Connection failed to node '{self.host}'")
        if is_dict(test) and test.get(STATUS) in [301, 302]:
            server_url = str(test.get(REDIRECTION))
            if not server_url.endswith(test_path):
                log_e("RudiNodeConnector", f"!! Node '{self.host}'", "redirection incorrect!")
                raise ConnectionError(f"Connection failed to node '{self.host}'")
            self._set_url(server_url.replace(f"/{test_path}", ""))
            test = self.request(test_path)
            if test is None:
                log_e("RudiNodeConnector", f"!! Node '{self.host}'", "redirection failed!")
                raise ConnectionError(f"Connection failed to node '{self.host}'")
            log_d("RudiNodeConnector", f"Node '{self.host}'", "redirection OK")

        else:
            log_d("RudiNodeConnector", f"Node '{self.host}'", "connection OK")

    def get_metadata_with_uuid(self, metadata_uuid: str):
        return self.get_api(f"resources/{metadata_uuid}")

    def get_metadata_with_filter(self, rudi_fields_filter: dict):
        filter_str = ""
        for i, (key, val) in enumerate(rudi_fields_filter.items()):
            # TODO: special cases of producer / contact / available_formats
            filter_str += f"&{key}={val}"

        return self.get_api(f"resources?{filter_str[1:]}")

    def get_metadata_count(self):
        return self.get_api("resources?limit=1")["total"]

    def get_metadata_list(self, max_number: int = 0):
        meta_nb = self.get_metadata_count()
        meta_set = []
        req_offset = 0
        if not max_number:
            max_number = meta_nb
        while req_offset < meta_nb and req_offset < max_number:
            req_limit = REQ_LIMIT if req_offset + REQ_LIMIT < max_number else max_number - req_offset
            meta_list_partial = self.get_api(f"resources?sort_by=-updatedAt&limit={req_limit}&offset={req_offset}")
            log_d("get_metadata_list", "total", meta_list_partial["total"])
            log_d("get_metadata_list", "len", len(meta_list_partial["items"]))
            meta_set += meta_list_partial["items"]
            req_offset += REQ_LIMIT
        return meta_set

    def get_metadata_ids(self):
        meta_list = self.get_api("resources?fields=global_id,resource_title")
        return meta_list["items"]

    def get_list_media_for_metadata(self, metadata_uuid):
        meta = self.get_metadata_with_uuid(metadata_uuid)
        media_list = meta["available_formats"]
        media_list_final = []
        for media in media_list:
            media_list_final.append(
                {
                    "url": media["connector"]["url"],
                    "type": media["media_type"],
                    "meta_contact": media["media_id"],
                    "id": media["media_id"],
                }
            )
        return media_list_final
