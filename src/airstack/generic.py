"""
Module: generic.py
Description: This module contains the generic methods required by this product.
"""

import re
from graphql.language.ast import Field, ObjectField, ObjectValue, StringValue, Name, Argument, FragmentSpread, InlineFragment, SelectionSet, Document
from graphql.language.visitor import Visitor
from graphql import parse, print_ast


def find_page_info(json_data):
    """Func to find the pageInfo from json response

    Args:
        json_data (dict): api response

    Returns:
        json: pageInfo
    """
    if isinstance(json_data, dict):
        if 'pageInfo' in json_data:
            return json_data['pageInfo']
        else:
            for value in json_data.values():
                page_info = find_page_info(value)
                if page_info:
                    return page_info
    elif isinstance(json_data, list):
        page_infos = []
        for item in json_data[0]:
            page_infos.append(find_page_info(json_data[0][item]))
        if page_infos:
            return page_infos
    return None


def modify_query_with_cursor(query, key, cursor):
    """Modify the GraphQL query by adding or replacing the cursor input for the specified key."""
    pattern = rf'(\b{key}\b[^}}]+cursor:\s")[^"]+'
    modified_query = re.sub(pattern, rf'\g<1>{cursor}', query)
    return modified_query


def create_object_field(name, value):
    """
    Func to create a object
    Args:
        name: name of the object
        value: value of the object

    Returns:

    """
    return ObjectField(name=Name(value=name), value=StringValue(value=value))


def add_cursor_to_input_field(ast, field_name, cursor_value):
    """
    Func to add cursor to input fields
    Args:
        ast: parsed ast
        field_name: field_name where to add
        cursor_value: cursor value

    Returns:

    """
    for definition in ast.definitions:
        if definition.operation == "query":
            for selection in definition.selection_set.selections:
                if isinstance(selection, Field):
                    if selection.name.value == field_name or (selection.alias and
                    selection.alias.value == field_name):
                        arguments = selection.arguments
                        if not arguments:
                            # If no arguments are present, create a new input argument
                            # with the cursor field
                            argument = Argument(
                                name=Name(value='input'),
                                value=ObjectValue(fields=[create_object_field('cursor',
                                cursor_value)])
                            )
                            selection.arguments.append(argument)
                        else:
                            # If input argument exists, check if it already has a cursor field
                            for argument in arguments:
                                if argument.name.value == 'input':
                                    input_value = argument.value
                                    for field in input_value.fields:
                                        if isinstance(field, ObjectField) and field.name.value == 'cursor':
                                            # If cursor field exists, replace its value
                                            field.value = StringValue(value=cursor_value)
                                            return  # Exit the loop if cursor field is found
                                    # If cursor field is not found, add it to the input fields
                                    cursor_field = create_object_field('cursor', cursor_value)
                                    input_value.fields.append(cursor_field)
                                    return  # Exit the loop if input argument is found
                        return


def replace_cursor_value(ast, key, cursor_value):
    """
    Func to replace cursor value
    Args:
        ast: parsed ast
        key: key to replace
        cursor_value: new cursor value

    Returns:

    """
    for definition in ast.definitions:
        if definition.operation == "query":
            for selection in definition.selection_set.selections:
                if isinstance(selection, Field) and selection.alias and selection.alias.value == key:
                    for argument in selection.arguments:
                        if argument.name.value == 'input':
                            input_value = argument.value
                            for field in input_value.fields:
                                if isinstance(field, ObjectField) and field.name.value == 'cursor':
                                    field.value = StringValue(value=cursor_value)
                                    return  # Exit the loop if cursor field is found
                            # If cursor field is not found, add it to the input fields
                            cursor_field = create_object_field('cursor', cursor_value)
                            input_value.fields.append(cursor_field)
                            return  # Exit the loop if input argument is found


def has_cursor(ast, key):
    """
    Func to check if dict has cursor
    Args:
        ast: parsed ast
        key: for which key to check

    Returns:

    """
    for definition in ast.definitions:
        if definition.operation == "query":
            for selection in definition.selection_set.selections:
                if isinstance(selection, Field) and selection.alias and selection.alias.value == key:
                    for argument in selection.arguments:
                        if argument.name.value == 'input':
                            input_value = argument.value
                            if isinstance(input_value, ObjectValue):
                                for field in input_value.fields:
                                    if field.name.value == 'cursor':
                                        return True
    return False

class RemoveQueryByStartingName(Visitor):
    """Class to remove queries from a multi-query that do not have next or prevCursor based on field names or aliases"""

    def __init__(self, query_start):
        self.query_start = query_start

    def enter_OperationDefinition(self, node, key, parent, path, ancestors):
        if node.operation == 'query':
            selections = node.selection_set.selections
            selections[:] = [selection for selection in selections if not self._should_remove_query(selection)]
            if not selections:
                # Remove variables when there are no remaining selections
                node.variable_definitions = None

    def _should_remove_query(self, selection):
        if isinstance(selection, FragmentSpread):
            return False
        if isinstance(selection, InlineFragment):
            return self._should_remove_query(selection.selection_set)
        if isinstance(selection, Field):
            field_name = selection.name.value
            alias_name = selection.alias.value if selection.alias else None
            if field_name.startswith(self.query_start) or (alias_name and alias_name.startswith(self.query_start)):
                return True
        return False

def add_page_info_to_queries(graphql_document):
    """Func to add page info to the graphql query

    Args:
        graphql_document (ast): parsed query

    Returns:
        str: page info added query
    """
    parsed_document = parse(graphql_document)
    modified_document = _add_page_info_to_queries(parsed_document)
    return print_ast(modified_document)

def _add_page_info_to_queries(node):
    if isinstance(node, Document):
        node.definitions = [_add_page_info_to_queries(definition) for
        definition in node.definitions]
    elif isinstance(node, Field):
        if node.selection_set is None:
            node.selection_set = SelectionSet(selections=[])
        node.selection_set.selections.append(Field(
            name=Name(value="pageInfo"),
            selection_set=SelectionSet(selections=[
                Field(name=Name(value="nextCursor")),
                Field(name=Name(value="prevCursor"))
            ])
        ))
    elif hasattr(node, "selection_set"):
        node.selection_set.selections = [_add_page_info_to_queries(selection) for
        selection in node.selection_set.selections]
    return node

def remove_unused_variables(document_ast, query):
    """Func to remove unused variables from the query

    Args:
        document_ast (ast): parsed query
        query (str): query
    """
    for definition in document_ast.definitions:
        for _count, _variable in enumerate(definition.variable_definitions):
            if query.count(_variable.variable.name.value) == 1:
                del document_ast.definitions[0].variable_definitions[_count]
    return print_ast(document_ast)
