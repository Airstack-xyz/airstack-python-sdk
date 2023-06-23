"""
Module: execute_query.py
Description: This module contains the methods to execute the query.
"""

import json
import warnings
import re
from graphql import parse, print_ast, visit
from airstack.send_request import SendRequest
from airstack.generic import (
    find_page_info,
    add_cursor_to_input_field,
    replace_cursor_value,
    has_cursor,
    RemoveQueryByStartingName,
    add_page_info_to_queries,
    remove_unused_variables
)
from airstack.constant import AirstackConstants

warnings.filterwarnings("ignore", message="coroutine .* was never awaited")

class QueryResponse:
    """Class for generate the query response
    """
    def __init__(self, response, status_code, error, has_next_page=None, has_prev_page=None,
    get_next_page=None, get_prev_page=None):
        """Init function

        Args:
            response (dic): query response
            status_code (int): status code
            error (str): error if there
            has_next_page (bool, optional): if next page is there. Defaults to None.
            has_prev_page (bool, optional): if previous page is there. Defaults to None.
            get_next_page (func, optional): func to get the next page data. Defaults to None.
            get_prev_page (func, optional): func to get the previous page data. Defaults to None.
        """
        self.data = response
        self.status_code = status_code
        self.error = error
        self.has_next_page = has_next_page
        self.has_prev_page = has_prev_page
        self.get_next_page = get_next_page
        self.get_prev_page = get_prev_page

class AirstackClient:
    """Class to create api client for airstack api's
    """

    def __init__(self, url=None, api_key=None):
        """Init function for api client

        Args:
            url (str, optional): base url for server. Defaults to None.
            api_key (str, required): api key. Defaults to None.

        Raises:
            ValueError: _description_
        """
        self.url = AirstackConstants.API_ENDPOINT_PROD if url is None else url
        if api_key is None:
            raise ValueError("API key must be provided.")

        self.timeout = AirstackConstants.API_TIMEOUT
        self.api_key = api_key

    def create_execute_query_object(self, query=None, variables=None):
        """Create execute query object for every query

        Args:
            query (str, optional): query. Defaults to None.
            variables (dict, optional): variables for the query. Defaults to None.

        Returns:
            object: execute query obiect
        """
        execute_query = ExecuteQuery(query=query, variables=variables, url=self.url,
        api_key=self.api_key, timeout=self.timeout)
        return execute_query

    def queries_object(self):
        """Create popular query object for popular queries

        Returns:
            object: execute popular query obiect
        """
        from airstack.popular_queries import ExecutePopularQueries
        execute_popular_query = ExecutePopularQueries(url=self.url,api_key=self.api_key,
        timeout=self.timeout)
        return execute_popular_query

class ExecuteQuery:
    """Class to execute query functions

    Returns:
        object: object of execute query
    """
    def __init__(self, query=None, variables=None, url=None, api_key=None, timeout=None):
        self.deleted_queries = []
        self.query = query
        self.variables = variables
        self.url = url
        self.api_key = api_key
        self.timeout = timeout

    async def execute_query(self, query=None):
        """Async function to run a GraphQL query and get the data

        Args:
            query (str): GraphQL query string. Defaults to None
            variables (dict, optional): Variables for the query. Defaults to
            None.

        Returns:
            Tuple: GraphQL response data or None, GraphQL response status code,
            error message or None
        """
        if query is None:
            query = self.query

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.api_key
        }
        payload = {
            'query': query,
            'variables': self.variables
        }

        response, status_code, error = await SendRequest.send_post_request(
            url=self.url, headers=headers, data=json.dumps(payload), timeout=self.timeout)
        return QueryResponse(response, status_code, error)

    async def execute_paginated_query(self, query=None, variables=None):
        """Async function to execute paginated query.

        Args:
            query (str): GraphQL query string. Defaults to None
            variables (dict, optional): Variables for the query. Defaults to
            None.

        Returns:
            Tuple: GraphQL response data or None, GraphQL response status code,
            error message or None, next cursor,
            previous cursor
        """
        if query is None:
            query = self.query

        regex = re.compile(r'pageInfo')
        has_page_info = regex.search(query)
        if has_page_info is None:
            query = add_page_info_to_queries(query)

        query_response = await self.execute_query(query=query)
        if query_response.error is not None:
            return QueryResponse(None, query_response.status_code, query_response.error,
            None, None, None, None)

        page_info = {}
        for _key, value in query_response.data.items():
            page_info[_key] = find_page_info(query_response.data[_key])

        has_next_page = any(page_info['nextCursor'] != '' for page_info in page_info.values())
        has_prev_page = any(page_info['prevCursor'] != '' for page_info in page_info.values())

        return QueryResponse(query_response.data, query_response.status_code,
                            query_response.error, has_next_page, has_prev_page,
                            self.get_next_page(query, variables, page_info),
                            self.get_prev_page(query, variables, page_info))

    async def get_next_page(self, query, variables, page_info):
        """Async function to get the next page data.

        Args:
            query (str): GraphQL query string.
            variables (dict): Variables for the query.
            page_info (dict): Page info dictionary.
            deleted_queries (list): List to store deleted queries.
            next_cursors (list): List to store next cursors.

        Returns:
            Tuple: GraphQL response data or None, GraphQL response status code,
            error message or None, next cursor,
            previous cursor
        """
        next_query = query
        stored = False
        for _page_info_key, _page_info_value in page_info.items():
            document_ast = parse(next_query)
            if _page_info_value['nextCursor'] == "":
                self.deleted_queries.append(next_query)
                stored = True
                visitor = RemoveQueryByStartingName(query_start=_page_info_key)
                document_ast = visit(document_ast, visitor)
                next_query = remove_unused_variables(document_ast=document_ast,
                query=print_ast(document_ast))
            else:
                if not stored:
                    self.deleted_queries.append(None)
                if has_cursor(document_ast, _page_info_key):
                    replace_cursor_value(document_ast, _page_info_key,
                    _page_info_value['nextCursor'])
                else:
                    add_cursor_to_input_field(document_ast, _page_info_key,
                    _page_info_value['nextCursor'])
                next_query = print_ast(document_ast)
        return await self.execute_paginated_query(next_query, variables)

    async def get_prev_page(self, query, variables, page_info):
        """Async function to get the previous page data.

        Args:
            query (str): GraphQL query string.
            variables (dict): Variables for the query.
            page_info (dict): Page info dictionary.

            Returns:
                Tuple: GraphQL response data or None, GraphQL response status code,
                error message or None, next cursor,
                previous cursor
            """
        deleted_query = self.deleted_queries.pop()
        if deleted_query:
            next_query = deleted_query
        else:
            next_query = query
        for _page_info_key, _page_info_value in page_info.items():
            document_ast = parse(next_query)
            if has_cursor(document_ast, _page_info_key):
                replace_cursor_value(document_ast, _page_info_key,
                _page_info_value['prevCursor'])
            else:
                add_cursor_to_input_field(document_ast, _page_info_key,
                _page_info_value['prevCursor'])
            next_query = print_ast(document_ast)
        return await self.execute_paginated_query(next_query, variables)
