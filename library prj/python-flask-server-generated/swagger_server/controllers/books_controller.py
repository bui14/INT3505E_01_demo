import connexion
import six

from swagger_server.models.book import Book  # noqa: E501
from swagger_server.models.book_input import BookInput  # noqa: E501
from swagger_server.models.book_response import BookResponse  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.paged_book_list import PagedBookList  # noqa: E501
from swagger_server import util


def api_v1_books_book_id_delete(book_id):  # noqa: E501
    """Xóa sách (Yêu cầu Admin)

     # noqa: E501

    :param book_id: ID của sách
    :type book_id: int

    :rtype: None
    """
    return 'do some magic!'


def api_v1_books_book_id_get(book_id):  # noqa: E501
    """Lấy chi tiết sách theo ID

     # noqa: E501

    :param book_id: ID của sách
    :type book_id: int

    :rtype: Book
    """
    return 'do some magic!'


def api_v1_books_book_id_put(body, book_id):  # noqa: E501
    """Cập nhật sách (Yêu cầu Admin)

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param book_id: ID của sách
    :type book_id: int

    :rtype: BookResponse
    """
    if connexion.request.is_json:
        body = BookInput.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def api_v1_books_get(offset=None, limit=None):  # noqa: E501
    """Lấy danh sách sách có phân trang Offset/Limit

     # noqa: E501

    :param offset: Vị trí bắt đầu của danh sách (số lượng bản ghi bỏ qua). Mặc định 0.
    :type offset: int
    :param limit: Số lượng bản ghi tối đa được trả về. Mặc định 10.
    :type limit: int

    :rtype: PagedBookList
    """
    return 'do some magic!'


def api_v1_books_post(body):  # noqa: E501
    """Thêm sách mới (Yêu cầu Admin)

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: BookResponse
    """
    if connexion.request.is_json:
        body = BookInput.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
