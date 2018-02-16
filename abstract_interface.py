from abc import ABCMeta, abstractmethod


__version__ = '0.0.1'
__author__ = 'Molly LeCompte'


class StorageInterface(metaclass=ABCMeta):

    def __init__(self):
        """

        """
        super().__init__()

    @abstractmethod
    def store_template(self, template):
        """
        Stores template
        :param template: dstream template
        :type template: dict
        :return:
        :rtype:
        """
        raise NotImplementedError("subclass must implement this abstract method.")

    @abstractmethod
    def retrieve_template_by_id(self, template_id):
        """
        Retrieves template by id
        :param template_id: the template id
        :type template_id:
        :return: dstream template
        :rtype: dict
        """
        raise NotImplementedError("subclass must implement this abstract method.")

    @abstractmethod
    def retrieve_current_template(self, stream_token):
        """
        Retrieves current template for stream by stream token
        :param stream_token: stream token
        :type stream_token: str
        :return:
        :rtype:
        """
        raise NotImplementedError("subclass must implement this abstract method.")

    @abstractmethod
    def store_bstream_data(self, bstream, token):
        """
        Stores bstream
        :param bstream: bstream dict
        :type bstream: dict
        :return:
        :rtype:
        """
        raise NotImplementedError("subclass must implement this abstract method.")

    @abstractmethod
    def retrieve_data(self, stream_token, **retrieval_args, **retrieval_kwargs):
        """
        Retrieves raw data, optionally within certain parameters i.e. timestamp range
        :param stream_token: stream token
        :type stream_token: str
        :param: retrieval_args: kind of data retrieved i.e. raw, filtered
        :param retrieval_kwargs: retrieval params i.e. start_ts=45945, end_ts=None
        :type retrieval_kwargs: dict
        :return: results
        :rtype: pandas df
        """
        raise NotImplementedError("subclass must implement this abstract method.")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~NON ABSTRACT

    def retrieve_all_current_templates(self, stream_tokens: list):
        templates = [self.retrieve_current_template(token) for token in stream_tokens]

        return templates