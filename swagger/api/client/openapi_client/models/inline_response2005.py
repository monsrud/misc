# coding: utf-8

"""
    Practice API for Learning Swagger

    Practice API for Learning Swagger  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Contact: marshall@theonsruds.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from openapi_client.configuration import Configuration


class InlineResponse2005(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'cpu_model': 'str',
        'cpu_mhz': 'float',
        'cpu_cores': 'int'
    }

    attribute_map = {
        'cpu_model': 'cpu_model',
        'cpu_mhz': 'cpu_mhz',
        'cpu_cores': 'cpu_cores'
    }

    def __init__(self, cpu_model=None, cpu_mhz=None, cpu_cores=None, local_vars_configuration=None):  # noqa: E501
        """InlineResponse2005 - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._cpu_model = None
        self._cpu_mhz = None
        self._cpu_cores = None
        self.discriminator = None

        if cpu_model is not None:
            self.cpu_model = cpu_model
        if cpu_mhz is not None:
            self.cpu_mhz = cpu_mhz
        if cpu_cores is not None:
            self.cpu_cores = cpu_cores

    @property
    def cpu_model(self):
        """Gets the cpu_model of this InlineResponse2005.  # noqa: E501


        :return: The cpu_model of this InlineResponse2005.  # noqa: E501
        :rtype: str
        """
        return self._cpu_model

    @cpu_model.setter
    def cpu_model(self, cpu_model):
        """Sets the cpu_model of this InlineResponse2005.


        :param cpu_model: The cpu_model of this InlineResponse2005.  # noqa: E501
        :type: str
        """

        self._cpu_model = cpu_model

    @property
    def cpu_mhz(self):
        """Gets the cpu_mhz of this InlineResponse2005.  # noqa: E501


        :return: The cpu_mhz of this InlineResponse2005.  # noqa: E501
        :rtype: float
        """
        return self._cpu_mhz

    @cpu_mhz.setter
    def cpu_mhz(self, cpu_mhz):
        """Sets the cpu_mhz of this InlineResponse2005.


        :param cpu_mhz: The cpu_mhz of this InlineResponse2005.  # noqa: E501
        :type: float
        """

        self._cpu_mhz = cpu_mhz

    @property
    def cpu_cores(self):
        """Gets the cpu_cores of this InlineResponse2005.  # noqa: E501


        :return: The cpu_cores of this InlineResponse2005.  # noqa: E501
        :rtype: int
        """
        return self._cpu_cores

    @cpu_cores.setter
    def cpu_cores(self, cpu_cores):
        """Sets the cpu_cores of this InlineResponse2005.


        :param cpu_cores: The cpu_cores of this InlineResponse2005.  # noqa: E501
        :type: int
        """

        self._cpu_cores = cpu_cores

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, InlineResponse2005):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, InlineResponse2005):
            return True

        return self.to_dict() != other.to_dict()
