"""
Module: execute_query.py
Description: This module contains the methods to execute the query.
"""

import json
import re
from graphql import parse, print_ast, visit
from airstack.send_request import SendRequest
from graphql.language.ast import OperationDefinition
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
        self.response = response
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

    async def execute_query(self, query=None, variables=None):
        """Async function to run a GraphQL query and get the data

        Args:
            query (str): GraphQL query string. Defaults to None
            variables (dict, optional): Variables for the query. Defaults to
            None.

        Returns:
            Tuple: GraphQL response data or None, GraphQL response status code,
            error message or None
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.api_key
        }
        payload = {
            'query': query,
            'variables': variables
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
        regex = re.compile(r'pageInfo')
        has_page_info = regex.search(query)
        if has_page_info is None:
            query = add_page_info_to_queries(query)

        query_response = await self.execute_query(query, variables)
        if query_response.error is not None:
            return QueryResponse(None, query_response.status_code, query_response.error, None, None, None, None)

        page_info = {}
        for _key, value in query_response.response.items():
            page_info[_key] = find_page_info(query_response.response[_key])

        has_next_page = any(page_info['nextCursor'] != '' for page_info in page_info.values())
        has_prev_page = any(page_info['prevCursor'] != '' for page_info in page_info.values())

        async def get_next_page():
            """Func to get the next page data

            Returns:
                Tuple: GraphQL response data or None, GraphQL response status code,
                error message or None, next cursor,
                previous cursor
            """
            next_query = query
            for _page_info_key, _page_info_value in page_info.items():
                document_ast = parse(next_query)
                if _page_info_value['nextCursor'] == "":
                    visitor = RemoveQueryByStartingName(query_start=_page_info_key)
                    document_ast = visit(document_ast, visitor)
                    next_query = remove_unused_variables(document_ast=document_ast, query=print_ast(document_ast))
                else:
                    if has_cursor(document_ast, _page_info_key):
                        replace_cursor_value(document_ast, _page_info_key,
                        _page_info_value['nextCursor'])
                    else:
                        add_cursor_to_input_field(document_ast, _page_info_key,
                        _page_info_value['nextCursor'])
                    next_query = print_ast(document_ast)
            return await self.execute_paginated_query(next_query, variables)

        async def get_prev_page():
            """Func to get the previous page data

            Returns:
                Tuple: GraphQL response data or None, GraphQL response status code,
                error message or None, next cursor,
                previous cursor
            """
            next_query = query
            for _page_info_key, _page_info_value in page_info.items():
                document_ast = parse(next_query)
                if _page_info_value['prevCursor'] == "":
                    visitor = RemoveQueryByStartingName(query_start=_page_info_key)
                    document_ast = visit(document_ast, visitor)
                    next_query = remove_unused_variables(document_ast=document_ast, query=print_ast(document_ast))
                else:
                    if has_cursor(document_ast, _page_info_key):
                        replace_cursor_value(document_ast, _page_info_key,
                        _page_info_value['prevCursor'])
                    else:
                        add_cursor_to_input_field(document_ast, _page_info_key,
                        _page_info_value['prevCursor'])
                    next_query = print_ast(document_ast)
            return await self.execute_paginated_query(next_query, variables)

        return QueryResponse(query_response.response, query_response.status_code,
        query_response.error,has_next_page, has_prev_page,get_next_page, get_prev_page)
