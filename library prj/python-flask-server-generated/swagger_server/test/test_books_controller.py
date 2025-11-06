# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.book import Book  # noqa: E501
from swagger_server.models.book_input import BookInput  # noqa: E501
from swagger_server.models.book_response import BookResponse  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.paged_book_list import PagedBookList  # noqa: E501
from swagger_server.test import BaseTestCase


class TestBooksController(BaseTestCase):
    """BooksController integration test stubs"""

    def test_api_v1_books_book_id_delete(self):
        """Test case for api_v1_books_book_id_delete

        Xóa sách (Yêu cầu Admin)
        """
        response = self.client.open(
            '/api/v1/books/{book_id}'.format(book_id=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_v1_books_book_id_get(self):
        """Test case for api_v1_books_book_id_get

        Lấy chi tiết sách theo ID
        """
        response = self.client.open(
            '/api/v1/books/{book_id}'.format(book_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_v1_books_book_id_put(self):
        """Test case for api_v1_books_book_id_put

        Cập nhật sách (Yêu cầu Admin)
        """
        body = BookInput()
        response = self.client.open(
            '/api/v1/books/{book_id}'.format(book_id=56),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_v1_books_get(self):
        """Test case for api_v1_books_get

        Lấy danh sách sách có phân trang Offset/Limit
        """
        query_string = [('offset', 1),
                        ('limit', 100)]
        response = self.client.open(
            '/api/v1/books',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_v1_books_post(self):
        """Test case for api_v1_books_post

        Thêm sách mới (Yêu cầu Admin)
        """
        body = BookInput()
        response = self.client.open(
            '/api/v1/books',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
