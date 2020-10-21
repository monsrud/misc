# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.inline_response200 import InlineResponse200  # noqa: E501
from openapi_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from openapi_server.models.inline_response2002 import InlineResponse2002  # noqa: E501
from openapi_server.models.inline_response2003 import InlineResponse2003  # noqa: E501
from openapi_server.models.inline_response2004 import InlineResponse2004  # noqa: E501
from openapi_server.models.inline_response2005 import InlineResponse2005  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_cpu_get(self):
        """Test case for cpu_get

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/practice/1.0.0/cpu',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_date_get(self):
        """Test case for date_get

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/practice/1.0.0/date',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_df_get(self):
        """Test case for df_get

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/practice/1.0.0/df',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_memory_get(self):
        """Test case for memory_get

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/practice/1.0.0/memory',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_uname_get(self):
        """Test case for uname_get

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/practice/1.0.0/uname',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_uptime_get(self):
        """Test case for uptime_get

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/practice/1.0.0/uptime',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
