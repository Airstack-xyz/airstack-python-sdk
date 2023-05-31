import re
from graphql.language.ast import Field, ObjectField, ObjectValue, StringValue, Name, Argument


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
