# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.auth_response import AuthResponse  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.login_input import LoginInput  # noqa: E501
from swagger_server.test import BaseTestCase


class TestAuthenticationController(BaseTestCase):
    """AuthenticationController integration test stubs"""

    def test_api_v1_auth_login_post(self):
        """Test case for api_v1_auth_login_post

        Đăng nhập và nhận JWT Token
        """
        body = LoginInput()
        response = self.client.open(
            '/api/v1/auth/login',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
