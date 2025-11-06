# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.test import BaseTestCase


class TestUtilityController(BaseTestCase):
    """UtilityController integration test stubs"""

    def test_api_v1_books_code_reading_time_get(self):
        """Test case for api_v1_books_code_reading_time_get

        Cung cấp mã JavaScript tính thời gian đọc (Code-On-Demand)
        """
        response = self.client.open(
            '/api/v1/books/code/reading-time',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
