# coding: utf-8

"""
    Practice API for Learning Swagger

    Practice API for Learning Swagger  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Contact: marshall@theonsruds.com
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest

import openapi_client
from openapi_client.api.default_api import DefaultApi  # noqa: E501
from openapi_client.rest import ApiException


class TestDefaultApi(unittest.TestCase):
    """DefaultApi unit test stubs"""

    def setUp(self):
        self.api = openapi_client.api.default_api.DefaultApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_cpu_get(self):
        """Test case for cpu_get

        """
        pass

    def test_date_get(self):
        """Test case for date_get

        """
        pass

    def test_df_get(self):
        """Test case for df_get

        """
        pass

    def test_memory_get(self):
        """Test case for memory_get

        """
        pass

    def test_uname_get(self):
        """Test case for uname_get

        """
        pass

    def test_uptime_get(self):
        """Test case for uptime_get

        """
        pass


if __name__ == '__main__':
    unittest.main()
