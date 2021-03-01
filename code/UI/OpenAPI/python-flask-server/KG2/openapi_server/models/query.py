# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.message import Message
from openapi_server import util

from openapi_server.models.message import Message  # noqa: E501

class Query(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, message=None, bypass_cache=None, asynchronous=None, max_results=None, page_size=None, page_number=None, operations=None):  # noqa: E501
        """Query - a model defined in OpenAPI

        :param message: The message of this Query.  # noqa: E501
        :type message: Message
        :param bypass_cache: The bypass_cache of this Query.  # noqa: E501
        :type bypass_cache: str
        :param asynchronous: The asynchronous of this Query.  # noqa: E501
        :type asynchronous: str
        :param max_results: The max_results of this Query.  # noqa: E501
        :type max_results: int
        :param page_size: The page_size of this Query.  # noqa: E501
        :type page_size: int
        :param page_number: The page_number of this Query.  # noqa: E501
        :type page_number: int
        :param operations: The operations of this Query.  # noqa: E501
        :type operations: object
        """
        self.openapi_types = {
            'message': Message,
            'bypass_cache': str,
            'asynchronous': str,
            'max_results': int,
            'page_size': int,
            'page_number': int,
            'operations': object
        }

        self.attribute_map = {
            'message': 'message',
            'bypass_cache': 'bypass_cache',
            'asynchronous': 'asynchronous',
            'max_results': 'max_results',
            'page_size': 'page_size',
            'page_number': 'page_number',
            'operations': 'operations'
        }

        self._message = message
        self._bypass_cache = bypass_cache
        self._asynchronous = asynchronous
        self._max_results = max_results
        self._page_size = page_size
        self._page_number = page_number
        self._operations = operations

    @classmethod
    def from_dict(cls, dikt) -> 'Query':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Query of this Query.  # noqa: E501
        :rtype: Query
        """
        return util.deserialize_model(dikt, cls)

    @property
    def message(self):
        """Gets the message of this Query.

        The query Message is a serialization of the user request. Content of the Message object depends on the intended TRAPI operation. For example, the fill operation requires a non-empty query_graph field as part of the Message, whereas other operations, e.g. overlay, require non-empty results and knowledge_graph fields.  # noqa: E501

        :return: The message of this Query.
        :rtype: Message
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this Query.

        The query Message is a serialization of the user request. Content of the Message object depends on the intended TRAPI operation. For example, the fill operation requires a non-empty query_graph field as part of the Message, whereas other operations, e.g. overlay, require non-empty results and knowledge_graph fields.  # noqa: E501

        :param message: The message of this Query.
        :type message: Message
        """
        if message is None:
            raise ValueError("Invalid value for `message`, must not be `None`")  # noqa: E501

        self._message = message

    @property
    def bypass_cache(self):
        """Gets the bypass_cache of this Query.

        Set to true in order to bypass any possible cached message and try to answer the query over again  # noqa: E501

        :return: The bypass_cache of this Query.
        :rtype: str
        """
        return self._bypass_cache

    @bypass_cache.setter
    def bypass_cache(self, bypass_cache):
        """Sets the bypass_cache of this Query.

        Set to true in order to bypass any possible cached message and try to answer the query over again  # noqa: E501

        :param bypass_cache: The bypass_cache of this Query.
        :type bypass_cache: str
        """

        self._bypass_cache = bypass_cache

    @property
    def asynchronous(self):
        """Gets the asynchronous of this Query.

        Set to true in order to receive an incomplete message_id if the query will take a while. Client can then periodically request that message_id for a status update and eventual complete message  # noqa: E501

        :return: The asynchronous of this Query.
        :rtype: str
        """
        return self._asynchronous

    @asynchronous.setter
    def asynchronous(self, asynchronous):
        """Sets the asynchronous of this Query.

        Set to true in order to receive an incomplete message_id if the query will take a while. Client can then periodically request that message_id for a status update and eventual complete message  # noqa: E501

        :param asynchronous: The asynchronous of this Query.
        :type asynchronous: str
        """

        self._asynchronous = asynchronous

    @property
    def max_results(self):
        """Gets the max_results of this Query.

        Maximum number of individual results to return  # noqa: E501

        :return: The max_results of this Query.
        :rtype: int
        """
        return self._max_results

    @max_results.setter
    def max_results(self, max_results):
        """Sets the max_results of this Query.

        Maximum number of individual results to return  # noqa: E501

        :param max_results: The max_results of this Query.
        :type max_results: int
        """

        self._max_results = max_results

    @property
    def page_size(self):
        """Gets the page_size of this Query.

        Split the results into pages with this number of results each  # noqa: E501

        :return: The page_size of this Query.
        :rtype: int
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """Sets the page_size of this Query.

        Split the results into pages with this number of results each  # noqa: E501

        :param page_size: The page_size of this Query.
        :type page_size: int
        """

        self._page_size = page_size

    @property
    def page_number(self):
        """Gets the page_number of this Query.

        Page number of results when the number of results exceeds the page_size  # noqa: E501

        :return: The page_number of this Query.
        :rtype: int
        """
        return self._page_number

    @page_number.setter
    def page_number(self, page_number):
        """Sets the page_number of this Query.

        Page number of results when the number of results exceeds the page_size  # noqa: E501

        :param page_number: The page_number of this Query.
        :type page_number: int
        """

        self._page_number = page_number

    @property
    def operations(self):
        """Gets the operations of this Query.

        Container for one or more Message objects or identifiers for one or more Messages along with a processing plan and options for how those messages should be processed and returned  # noqa: E501

        :return: The operations of this Query.
        :rtype: object
        """
        return self._operations

    @operations.setter
    def operations(self, operations):
        """Sets the operations of this Query.

        Container for one or more Message objects or identifiers for one or more Messages along with a processing plan and options for how those messages should be processed and returned  # noqa: E501

        :param operations: The operations of this Query.
        :type operations: object
        """

        self._operations = operations