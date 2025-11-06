# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.paged_review_list import PagedReviewList  # noqa: E501
from swagger_server.models.review_input import ReviewInput  # noqa: E501
from swagger_server.models.review_response import ReviewResponse  # noqa: E501
from swagger_server.test import BaseTestCase


class TestReviewsController(BaseTestCase):
    """ReviewsController integration test stubs"""

    def test_api_v1_books_book_id_reviews_get(self):
        """Test case for api_v1_books_book_id_reviews_get

        Lấy danh sách nhận xét của một cuốn sách (có phân trang)
        """
        query_string = [('offset', 1),
                        ('limit', 100)]
        response = self.client.open(
            '/api/v1/books/{book_id}/reviews'.format(book_id=56),
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_v1_books_book_id_reviews_post(self):
        """Test case for api_v1_books_book_id_reviews_post

        Thêm nhận xét mới cho sách (Yêu cầu Đăng nhập)
        """
        body = ReviewInput()
        response = self.client.open(
            '/api/v1/books/{book_id}/reviews'.format(book_id=56),
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
