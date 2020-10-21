# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server import util


class InlineResponse200(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, uptime=None):  # noqa: E501
        """InlineResponse200 - a model defined in OpenAPI

        :param uptime: The uptime of this InlineResponse200.  # noqa: E501
        :type uptime: str
        """
        self.openapi_types = {
            'uptime': str
        }

        self.attribute_map = {
            'uptime': 'uptime'
        }

        self._uptime = uptime

    @classmethod
    def from_dict(cls, dikt) -> 'InlineResponse200':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The inline_response_200 of this InlineResponse200.  # noqa: E501
        :rtype: InlineResponse200
        """
        return util.deserialize_model(dikt, cls)

    @property
    def uptime(self):
        """Gets the uptime of this InlineResponse200.


        :return: The uptime of this InlineResponse200.
        :rtype: str
        """
        return self._uptime

    @uptime.setter
    def uptime(self, uptime):
        """Sets the uptime of this InlineResponse200.


        :param uptime: The uptime of this InlineResponse200.
        :type uptime: str
        """

        self._uptime = uptime
