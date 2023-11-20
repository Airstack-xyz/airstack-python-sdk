"""
Module: generic.py
Description: This module contains the generic methods required by this product.
"""

import re
from graphql.language.ast import Field, ObjectField, ObjectValue, StringValue, Name, Argument, FragmentSpread, InlineFragment, SelectionSet, Document
from graphql.language.visitor import Visitor
from graphql import parse, print_ast
from configurations.conf import default_score_map, BURNED_ADDRESSES


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
                                            field.value = StringValue(
                                                value=cursor_value)
                                            return  # Exit the loop if cursor field is found
                                    # If cursor field is not found, add it to the input fields
                                    cursor_field = create_object_field(
                                        'cursor', cursor_value)
                                    input_value.fields.append(cursor_field)
                                    return  # Exit the loop if input argument is found
                        return


def replace_cursor_value(ast, key, cursor_value, variables):
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
                                    if 'name' in field.value._fields:
                                        _replaced_value = field.value.name.value
                                        if _replaced_value in variables.keys():
                                            variables[_replaced_value] = cursor_value
                                    else:
                                        field.value = StringValue(
                                            value=cursor_value)
                                    return  # Exit the loop if cursor field is found
                            # If cursor field is not found, add it to the input fields
                            cursor_field = create_object_field(
                                'cursor', cursor_value)
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
            selections[:] = [
                selection for selection in selections if not self._should_remove_query(selection)]
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


def format_poaps_data(poaps, existing_user=None):
    if existing_user is None:
        existing_user = []

    recommended_users = existing_user.copy()
    for poap in poaps or []:
        attendee = poap.get('attendee', {})
        poap_event = poap.get('poapEvent', {})
        event_id = poap.get('eventId')

        name = poap_event.get('eventName')
        content_value = poap_event.get('contentValue', {})
        addresses = attendee.get('owner', {}).get('addresses', [])

        existing_user_index = -1
        for index, recommended_user in enumerate(recommended_users):
            recommended_user_addresses = recommended_user.get('addresses', [])
            if any(addr in recommended_user_addresses for addr in addresses):
                existing_user_index = index
                break

        image = content_value.get('image', {}).get(
            'extraSmall') if content_value.get('image') else None

        new_poap = {
            'name': name,
            'image': image,
            'eventId': event_id
        }

        if existing_user_index != -1:
            recommended_user = recommended_users[existing_user_index]
            _addresses = set(recommended_user.get('addresses', []))
            _addresses.update(addresses)
            recommended_user['addresses'] = list(_addresses)

            _poaps = recommended_user.get('poaps', [])
            if event_id and all(poap['eventId'] != event_id for poap in _poaps):
                _poaps.append(new_poap)
            recommended_user['poaps'] = _poaps
        else:
            new_user = attendee.get('owner', {})
            new_user['poaps'] = [new_poap]
            recommended_users.append(new_user)

    return recommended_users


def format_farcaster_followings_data(followings, existing_user=None):
    if existing_user is None:
        existing_user = []

    recommended_users = existing_user.copy()
    for following in followings:
        existing_user_index = -1
        for index, recommended_user in enumerate(recommended_users):
            recommended_user_addresses = recommended_user.get('addresses', [])
            if any(addr in recommended_user_addresses for addr in following.get('addresses', [])):
                existing_user_index = index
                break

        mutual_follower = following.get('mutualFollower', {})
        follower = mutual_follower.get(
            'Follower') if mutual_follower is not None else []
        follows_back = bool(follower[0]) if follower else False

        if existing_user_index != -1:
            follows = recommended_users[existing_user_index].get('follows', {})
            recommended_users[existing_user_index] = {
                **following,
                **recommended_users[existing_user_index],
                'follows': {
                    **follows,
                    'followingOnFarcaster': True,
                    'followedOnFarcaster': follows_back
                }
            }
        else:
            recommended_users.append({
                **following,
                'follows': {
                    'followingOnFarcaster': True,
                    'followedOnFarcaster': follows_back
                }
            })

    return recommended_users


def format_lens_followings_data(followings, existing_user=None):
    if existing_user is None:
        existing_user = []

    recommended_users = existing_user.copy()
    for following in followings:
        existing_user_index = -1
        for index, recommended_user in enumerate(recommended_users):
            recommended_user_addresses = recommended_user.get('addresses', [])
            if any(address in recommended_user_addresses for address in following.get('addresses', [])):
                existing_user_index = index
                break

        mutual_follower = following.get('mutualFollower', {})
        follower = mutual_follower.get(
            'Follower', []) if mutual_follower is not None else []
        follows_back = bool(follower[0]) if follower else False

        if existing_user_index != -1:
            follows = recommended_users[existing_user_index].get('follows', {})
            recommended_users[existing_user_index].update({
                **following,
                'follows': {
                    **follows,
                    'followingOnLens': True,
                    'followedOnLens': follows_back
                }
            })
        else:
            recommended_users.append({
                **following,
                'follows': {
                    'followingOnLens': True,
                    'followedOnLens': follows_back
                }
            })

    return recommended_users


def format_farcaster_followers_data(followers, existing_user=None):
    if existing_user is None:
        existing_user = []

    recommended_users = existing_user.copy()

    for follower in followers:
        existing_user_index = -1
        for index, recommended_user in enumerate(recommended_users):
            recommended_user_addresses = recommended_user.get('addresses', [])
            if any(address in follower.get('addresses', []) for address in recommended_user_addresses):
                existing_user_index = index
                break

        following = bool(follower.get('mutualFollower', {}).get('Following'))

        if existing_user_index != -1:
            follows = recommended_users[existing_user_index].get('follows', {})

            follows['followedOnFarcaster'] = True
            follows['followingOnFarcaster'] = follows.get(
                'followingOnFarcaster', False) or following

            recommended_users[existing_user_index].update({
                **follower,
                'follows': follows
            })
        else:
            recommended_users.append({
                **follower,
                'follows': {
                    'followingOnFarcaster': following,
                    'followedOnFarcaster': True
                }
            })

    return recommended_users


def format_lens_followers_data(followers, existing_user=None):
    if existing_user is None:
        existing_user = []

    recommended_users = existing_user.copy()

    for follower in followers:
        existing_user_index = -1
        for index, recommended_user in enumerate(recommended_users):
            recommended_user_addresses = recommended_user.get('addresses', [])
            if any(address in follower.get('addresses', []) for address in recommended_user_addresses):
                existing_user_index = index
                break

        following = bool(follower.get('mutualFollower', {}).get('Following'))

        if existing_user_index != -1:
            follows = recommended_users[existing_user_index].get('follows', {})

            follows['followedOnLens'] = True
            follows['followingOnLens'] = follows.get(
                'followingOnLens', False) or following

            recommended_users[existing_user_index].update({
                **follower,
                'follows': follows
            })
        else:
            recommended_users.append({
                **follower,
                'follows': {
                    'followingOnLens': following,
                    'followedOnLens': True
                }
            })

    return recommended_users


def format_token_sent_data(data, recommended_users=None):
    if recommended_users is None:
        recommended_users = []

    for transfer in data:
        addresses = transfer.get('addresses', [])
        existing_user_index = next((index for index, recommended_user in enumerate(recommended_users)
                                    if any(address in recommended_user.get('addresses', []) for address in addresses)), -1)

        token_transfers = {'sent': True}

        if existing_user_index != -1:
            existing_addresses = recommended_users[existing_user_index].get(
                'addresses', [])
            unique_addresses = list(set(existing_addresses + addresses))
            recommended_users[existing_user_index]['addresses'] = unique_addresses
            existing_token_transfers = recommended_users[existing_user_index].get(
                'tokenTransfers', {})
            recommended_users[existing_user_index]['tokenTransfers'] = {
                **existing_token_transfers, **token_transfers}
        else:
            recommended_users.append(
                {**transfer, 'tokenTransfers': token_transfers})

    return recommended_users


def format_token_received_data(data, _recommended_users=None):
    if _recommended_users is None:
        _recommended_users = []

    recommended_users = _recommended_users.copy()

    for transfer in data:
        addresses = transfer.get('addresses', []) if transfer else []
        existing_user_index = -1

        for index, recommended_user in enumerate(recommended_users):
            recommended_user_addresses = recommended_user.get('addresses', [])
            if any(address in recommended_user_addresses for address in addresses):
                existing_user_index = index
                break

        _token_transfers = {'received': True}

        if existing_user_index != -1:
            _addresses = recommended_users[existing_user_index].get(
                'addresses', [])
            new_addresses = list(set(_addresses + addresses))
            recommended_users[existing_user_index]['addresses'] = new_addresses
            existing_token_transfers = recommended_users[existing_user_index].get(
                'tokenTransfers', {})
            recommended_users[existing_user_index]['tokenTransfers'] = {
                **existing_token_transfers, **_token_transfers}
        else:
            new_user = transfer.copy() if transfer else {}
            new_user['tokenTransfers'] = _token_transfers
            recommended_users.append(new_user)

    return recommended_users


def format_eth_nft_data(data, _recommended_users=None):
    if _recommended_users is None:
        _recommended_users = []

    recommended_users = _recommended_users.copy()

    for nft in data or []:
        owner = nft.get('owner') if nft else {}
        token = nft.get('token') if nft else {}

        name = token.get('name')
        logo = token.get('logo', {})
        address = token.get('address')
        token_nfts = token.get('tokenNfts', [])
        addresses = owner.get('addresses', [])
        token_nft = token_nfts[0] if len(token_nfts) > 0 else None

        existing_user_index = -1
        for index, recommended_user in enumerate(recommended_users):
            recommended_user_addresses = recommended_user.get('addresses', [])
            if any(addr in addresses for addr in recommended_user_addresses):
                existing_user_index = index
                break

        if existing_user_index != -1:
            _addresses = recommended_users[existing_user_index].get(
                'addresses', [])
            _addresses.extend(addresses)
            _addresses = list(set(_addresses))  # Remove duplicates
            recommended_users[existing_user_index]['addresses'] = _addresses

            _nfts = recommended_users[existing_user_index].get('nfts', [])
            nft_exists = any(nft['address'] == address for nft in _nfts)
            if not nft_exists:
                _nfts.append({
                    'name': name,
                    'image': logo.get('small'),
                    'blockchain': 'ethereum',
                    'address': address,
                    'tokenNfts': token_nft
                })
            recommended_users[existing_user_index]['nfts'] = _nfts
        else:
            recommended_users.append({
                **owner,
                'nfts': [{
                    'name': name,
                    'image': logo.get('small'),
                    'blockchain': 'ethereum',
                    'address': address,
                    'tokenNfts': token_nft
                }]
            })

    return recommended_users


def format_polygon_nft_data(data, _recommended_users=None):
    if _recommended_users is None:
        _recommended_users = []

    recommended_users = _recommended_users.copy()

    for nft in data or []:
        owner = nft.get('owner', {})
        token = nft.get('token', {})

        name = token.get('name')
        logo = token.get('logo', {})
        address = token.get('address')
        token_nfts = token.get('tokenNfts', [])
        addresses = owner.get('addresses', [])
        token_nft = token_nfts[0] if len(token_nfts) > 0 else None

        existing_user_index = -1
        for index, recommended_user in enumerate(recommended_users):
            recommended_user_addresses = recommended_user.get('addresses', [])
            if any(addr in recommended_user_addresses for addr in addresses):
                existing_user_index = index
                break

        if existing_user_index != -1:
            _addresses = recommended_users[existing_user_index].get(
                'addresses', [])
            _addresses.extend(addresses)
            _addresses = list(set(_addresses))  # Remove duplicates
            recommended_users[existing_user_index]['addresses'] = _addresses

            _nfts = recommended_users[existing_user_index].get('nfts', [])
            nft_exists = any(nft['address'] == address for nft in _nfts)
            if not nft_exists:
                _nfts.append({
                    'name': name,
                    'image': logo.get('small'),
                    'blockchain': 'polygon',
                    'address': address,
                    'tokenNfts': token_nfts
                })
            recommended_users[existing_user_index]['nfts'] = _nfts
        else:
            recommended_users.append({
                **owner,
                'nfts': [{
                    'name': name,
                    'image': logo.get('small'),
                    'blockchain': 'polygon',
                    'address': address,
                    'tokenNfts': token_nfts
                }]
            })

    return recommended_users


def identity_map(users):
    identity_dict = {}
    for user in users:
        # Assuming user is a dictionary and has an 'id' field of a hashable type (e.g., string or int)
        user_id = user.get('id')
        if user_id is not None:
            identity_dict[user_id] = True
    return identity_dict


def is_burned_address(address):
    if not address:
        return False
    address = address.lower()
    return address in BURNED_ADDRESSES


def calculating_score(user, score_map=None):
    if score_map is None:
        score_map = default_score_map

    identities = [user]
    identity_dict = identity_map(identities)

    addresses = user.get('addresses', [])
    domains = user.get('domains', [])

    # Ensure addresses is a list
    if not isinstance(addresses, list):
        addresses = []

    # Ensure domains is a list of dictionaries
    if domains is not None or not isinstance(domains, list) or not all(isinstance(domain, dict) for domain in domains):
        domains = []

    if any(address in identity_dict for address in addresses if address is not None) or \
       any(domain.get('name') in identity_dict for domain in domains if domain is not None) or \
       any(is_burned_address(address) for address in addresses if address is not None):
        return None

    score = 0
    follows = user.get('follows', {})
    token_transfers = user.get('tokenTransfers', {})

    for key in ['followingOnLens', 'followedOnLens', 'followingOnFarcaster', 'followedOnFarcaster']:
        score += follows.get(key, 0) * score_map.get(key, 0)

    for key in ['sent', 'received']:
        score += token_transfers.get(key, 0) * \
            score_map.get('token' + key.capitalize(), 0)

    unique_nfts = {f"{nft['address']}-{nft.get('tokenNfts', {}).get('tokenId')}" for nft in user.get(
        'nfts', []) if not is_burned_address(nft['address'])}
    eth_nft_count = sum(1 for nft in unique_nfts if 'ethereum' in nft)
    polygon_nft_count = sum(1 for nft in unique_nfts if 'polygon' in nft)

    score += (score_map['commonEthNfts'] * eth_nft_count) + \
        (score_map['commonPolygonNfts'] * polygon_nft_count)

    poaps = user.get('poaps', [])
    score += score_map['commonPoaps'] * len(poaps)

    user['_score'] = score
    return user
