from os.path import isdir, abspath
from typing import Union

from conf_read.connectors_conf_reader import ConnectorConfReader
from lib_rudi_io.io_rudi_api import RudiNodeConnector
from utils.dict_utils import safe_get_key, find_in_dict_list, filter_dict_list
from utils.http_utils import https_download
from utils.log import log_d
from utils.string_utils import slash_join


class RudiNodeGetter:
    _default_getter = None

    def __init__(self, server_url: str, headers_user_agent: str = 'RudiNodeGet'):
        self._server_url = server_url
        self._headers_user_agent = headers_user_agent

        self._connector = None

        self._meta_list = None
        self._meta_count = 0
        self._org_list = None
        self._org_names = None
        self._contact_list = None
        self._contact_names = None
        self._themes = None
        self._keywords = None

    def _reset_cache(self) -> None:
        """
        Resets the cached metadata
        """
        self._meta_list = None
        self._meta_count = 0
        self._org_list = None
        self._org_names = None
        self._contact_list = None
        self._contact_names = None
        self._themes = None
        self._keywords = None

    @property
    def server_url(self) -> str:
        """
        :return: the URL of the RUDI Producer node
        """
        return self._server_url

    @property
    def connector(self) -> RudiNodeConnector:
        if not self._connector:
            self._connector = RudiNodeConnector(self._server_url, self._headers_user_agent)
        return self._connector

    def connect(self, server_url: str, headers_user_agent: str = 'RudiNodeGet') -> None:
        """
        Reinitialize the connection to a RUDI node
        :param server_url: the URL of the RUDI node
        :param headers_user_agent: (optional) a way to identify the requests made to the node
        """
        self._server_url = server_url
        self._headers_user_agent = headers_user_agent
        self._connector = RudiNodeConnector(self._server_url, self._headers_user_agent)
        self._reset_cache()

    @property
    def metadata_count(self) -> int:
        """
        :return: the number of metadata stored on the RUDI Producer node
        """
        if not self._meta_count:
            self._meta_count = self.connector.get_metadata_count()
        return self._meta_count

    @property
    def metadata_list(self) -> list[dict]:
        """
        :return: the full list of the metadata stored on the RUDI Producer node
        """
        if not self._meta_list:
            self._meta_list = self.connector.get_metadata_list()
        return self._meta_list

    @property
    def organization_list(self) -> list[dict]:
        """
        :return: the list of the organizations (both data producer and metadata publisher) that appear in the metadata
        """
        if not self._org_list:
            self._org_list = []
            for meta in self.metadata_list:
                producer_info = safe_get_key(meta, 'producer')
                publisher_info = safe_get_key(meta, 'metadata_info', 'metadata_provider')

                producer_id = safe_get_key(producer_info, 'organization_id')
                was_producer_found = not producer_id

                publisher_id = safe_get_key(publisher_info, 'organization_id')
                was_publisher_found = not publisher_id or publisher_id == producer_id

                for org in self._org_list:
                    if was_producer_found and was_publisher_found:
                        break
                    org_id = safe_get_key(org, 'organization_id')
                    if not was_producer_found and org_id == producer_id:
                        was_producer_found = True
                    if not was_publisher_found and org_id == publisher_id:
                        was_publisher_found = True

                if not was_producer_found:
                    self._org_list.append(producer_info)
                if not was_publisher_found:
                    self._org_list.append(publisher_info)

        return self._org_list

    @property
    def organization_names(self) -> list[str]:
        """
        :return: the list of the names of the organizations (both data producer and metadata publisher) that appear in
        the metadata
        """
        if not self._org_names:
            self._org_names = []
            for org in self.organization_list:
                self._org_names.append(safe_get_key(org, 'organization_name'))
        self._org_names.sort()
        return self._org_names

    @property
    def contact_list(self) -> list[dict]:
        """
        :return: the list of the contacts declared in the RUDI node metadata
        """
        if not self._contact_list:
            self._contact_list = []
            for meta in self.metadata_list:
                meta_contacts = safe_get_key(meta, 'contacts')
                publ_contacts = safe_get_key(meta, 'metadata_info', 'metadata_contacts')
                if publ_contacts:
                    meta_contacts = meta_contacts + publ_contacts

                if meta_contacts:
                    for prod_contact in meta_contacts:
                        prod_contact_id = safe_get_key(prod_contact, 'contact_id')
                        if prod_contact_id:
                            if not find_in_dict_list(self._contact_list, {'contact_id': prod_contact_id}):
                                self._contact_list.append(prod_contact)

        return self._contact_list

    @property
    def contact_names(self) -> list[str]:
        """
        :return: the list of the names of the contacts declared in the RUDI node metadata
        """
        if not self._contact_names:
            self._contact_names = []
            for contact in self.contact_list:
                self._contact_names.append(safe_get_key(contact, 'contact_name'))
        self._contact_names.sort()
        return self._contact_names

    @property
    def themes(self) -> list[str]:
        """
        :return: the list of the themes declared in the RUDI node metadata
        """
        if not self._themes:
            self._themes = []
            for meta in self.metadata_list:
                theme = safe_get_key(meta, 'theme')
                if theme and theme not in self._themes:
                    self._themes.append(theme)
        self._themes.sort()
        return self._themes

    @property
    def keywords(self) -> list[str]:
        """
        :return: the list of the keywords declared in the RUDI node metadata
        """
        if not self._keywords:
            self._keywords = []
            for meta in self.metadata_list:
                keywords = safe_get_key(meta, 'keywords')
                if keywords:
                    for kw in keywords:
                        if kw not in self._keywords:
                            self._keywords.append(kw)
        self._keywords.sort()
        return self._keywords

    def filter_metadata(self, matching_filter: dict) -> dict:
        """
        Returns an object with the following attributes:
        - total: the number of metadata that match the filter
        - items: the list of the metadata that match the filter
        :param matching_filter: an object whose attributes will all be matched in the resulting metadata list
        :return: list of the metadata that atch the filter
        """
        items = filter_dict_list(self.metadata_list, matching_filter)
        total = len(items)
        return {'total': total, 'items': items}

    def get_metadata_with_producer(self, producer_name: str):
        return self.filter_metadata({'producer': {'organization_name': producer_name}})

    def get_metadata_with_contact(self, contact_name: str):
        return self.filter_metadata({'contacts': [{'contact_name': contact_name}]})

    def get_metadata_with_theme(self, theme: str):
        return self.filter_metadata({'theme': theme})

    def get_metadata_with_keyword(self, keyword: Union[str, list]):
        return self.filter_metadata({'keywords': keyword})

    def get_metadata_with_id(self, metadata_id):
        return find_in_dict_list(self.metadata_list, {'global_id': metadata_id})

    def download_media_for_metadata(self, meta, local_download_dir):
        if not isdir(local_download_dir):
            raise FileNotFoundError(f"The following folder does not exist: '{local_download_dir}'")

        meta = self.get_metadata_with_id(meta)
        media_list = safe_get_key(meta, 'available_formats')
        if not media_list:
            return None
        file_list = {'downloaded': [], 'missing': [], 'skipped': []}
        for media in media_list:
            media_type = safe_get_key(media, 'media_type')
            media_name = safe_get_key(media, 'media_name')
            media_url = safe_get_key(media, 'connector', 'url')
            if media_type != 'FILE':
                log_d('download_media_for_metadata', f"skipping media '{media_type}'", media['media_id'])
                file_info = {'media_name': media_name, 'media_url': media_url,
                             'media_id': safe_get_key(media, 'media_id'), 'media_type': media_type}
                file_list['skipped'].append(file_info)
            else:
                file_storage_status = safe_get_key(media, 'file_storage_status')

                if file_storage_status == 'available':
                    destination_path = abspath(slash_join(local_download_dir, media_name))
                    content = https_download(media_url)
                    open(destination_path, 'wb').write(content)
                    log_d('download_media_for_metadata', 'content saved to file', destination_path)
                    file_info = {'media_name': media_name, 'media_url': media_url,
                                 'media_id': safe_get_key(media, 'media_id'),
                                 'file_type': safe_get_key(media, 'file_type'),
                                 'created': safe_get_key(media, 'media_dates', 'created'),
                                 'updated': safe_get_key(media, 'media_dates', 'updated'),
                                 'file_path': destination_path}
                    log_d('download_media_for_metadata', 'file_info', file_info)
                    file_list['downloaded'].append(file_info)
                else:
                    file_info = {'media_name': media_name, 'media_url': media_url,
                                 'media_id': safe_get_key(media, 'media_id'),
                                 'file_type': safe_get_key(media, 'file_type'), 'status': file_storage_status}
                    file_list['missing'].append(file_info)
        return file_list

    @staticmethod
    def get_default():
        if RudiNodeGetter._default_getter is None:
            rudi_api_conf = ConnectorConfReader.get_defaults()
            RudiNodeGetter._default_getter = RudiNodeGetter(server_url=rudi_api_conf.rudi_node_url)
        return RudiNodeGetter._default_getter


if __name__ == '__main__':
    rudi_node_getter = RudiNodeGetter.get_default()
    log_d('RudiNodeConnector', 'metadata nb',
          rudi_node_getter.metadata_count)  # log_d('RudiNodeConnector', 'metadata nb', rudi_node_getter.metadata_list)
    log_d('RudiNodeConnector', 'organizations', rudi_node_getter.organization_list)
    log_d('RudiNodeConnector', 'organization names', rudi_node_getter.organization_names)
    log_d('RudiNodeConnector', 'contact names', rudi_node_getter.contact_names)
    log_d('RudiNodeConnector', 'themes', rudi_node_getter.themes)
    log_d('RudiNodeConnector', 'keywords', rudi_node_getter.keywords)
    log_d('RudiNodeConnector', 'filter_metadata', rudi_node_getter.filter_metadata(
        {'producer': {'organization_id': '1d6bc543-07ed-46f6-a813-958edb73d5f0', 'organization_name': 'SIB (Test)'}}))
    log_d('RudiNodeConnector', 'metadata_from_producer', rudi_node_getter.get_metadata_with_producer('SIB (Test)'))
    log_d('RudiNodeConnector', 'metadata_with_theme', rudi_node_getter.get_metadata_with_theme('citizenship'))
    kw = ['répartition', 'Commune']
    log_d('RudiNodeConnector', f"metadata_with_keyword '{kw}'", rudi_node_getter.get_metadata_with_keyword(kw))
    cont = 'Bacasable'
    log_d('RudiNodeConnector', f"metadata_with_contact '{cont}'", rudi_node_getter.get_metadata_with_contact(cont))
    meta_id = 'f48b4bcd-bba3-47ba-86e6-c0754b748728'
    # meta_id = '050d3ba5-7b35-4e25-8b86-5461a0428fbe'
    log_d('RudiNodeConnector', f"metadata_with_id '{meta_id}'", rudi_node_getter.get_metadata_with_id(meta_id))
    log_d('RudiNodeConnector', f"download_media_for_metadata '{meta_id}'",
          rudi_node_getter.download_media_for_metadata(meta_id, '../1-dwnld'))
