import connexion
import six

from swagger_server.models.auth_response import AuthResponse  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.login_input import LoginInput  # noqa: E501
from swagger_server import util


def api_v1_auth_login_post(body):  # noqa: E501
    """Đăng nhập và nhận JWT Token

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: AuthResponse
    """
    if connexion.request.is_json:
        body = LoginInput.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
