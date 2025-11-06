import connexion
import six

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.paged_review_list import PagedReviewList  # noqa: E501
from swagger_server.models.review_input import ReviewInput  # noqa: E501
from swagger_server.models.review_response import ReviewResponse  # noqa: E501
from swagger_server import util


def api_v1_books_book_id_reviews_get(book_id, offset=None, limit=None):  # noqa: E501
    """Lấy danh sách nhận xét của một cuốn sách (có phân trang)

     # noqa: E501

    :param book_id: ID của sách
    :type book_id: int
    :param offset: Vị trí bắt đầu của danh sách (số lượng bản ghi bỏ qua). Mặc định 0.
    :type offset: int
    :param limit: Số lượng bản ghi tối đa được trả về. Mặc định 10.
    :type limit: int

    :rtype: PagedReviewList
    """
    return 'do some magic!'


def api_v1_books_book_id_reviews_post(body, book_id):  # noqa: E501
    """Thêm nhận xét mới cho sách (Yêu cầu Đăng nhập)

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param book_id: ID của sách
    :type book_id: int

    :rtype: ReviewResponse
    """
    if connexion.request.is_json:
        body = ReviewInput.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
