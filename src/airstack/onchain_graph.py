"""
Module: onchain_graph.py
Description: This module contains the methods of Onchain Graphs.
"""

from airstack.constant import SocialsDappName, TransferType, ChainType
from airstack.generic import format_poaps_data, format_socials_followings_data, format_socials_followers_data, format_token_sent_data, format_token_received_data, format_eth_nft_data, format_polygon_nft_data, calculating_score
import traceback
from utility.custom_exception import AirstackException
import json


class ExecuteOnchainGraph():
    """Class to generate onchain graph data of a user
    """

    def __init__(self, create_execute_query_object=None) -> None:
        """Init function

        Args:
            create_execute_query_object (func): function to create execute query object from Airstack client class.
        """
        self.create_execute_query_object = create_execute_query_object

    async def _fetch_poaps_data(self, address: str, existing_users: list = []) -> list:
        """Async function to fetch all common POAP holders of a user

        Args:
            address (str): user's address
            existing_users (list, optional): Existing onchain graph data. Defaults to
            None.

        Returns:
            list: Concatenated list of existing onchain graph users with all common POAP holders
        """
        try:
            user_poaps_event_ids_query = """
            query MyQuery($user: Identity!) {
            Poaps(input: {filter: {owner: {_eq: $user}}, blockchain: ALL}) {
                Poap {
                eventId
                poapEvent {
                    isVirtualEvent
                }
                }
            }
            }
            """

            poaps_by_event_ids_query = """
            query MyQuery($eventIds: [String!]) {
            Poaps(input: {filter: {eventId: {_in: $eventIds}}, blockchain: ALL}) {
                Poap {
                eventId
                poapEvent {
                    eventName
                    contentValue {
                    image {
                        extraSmall
                    }
                    }
                }
                attendee {
                    owner {
                    addresses
                    domains {
                        name
                        isPrimary
                    }
                    socials {
                        dappName
                        blockchain
                        profileName
                        profileImage
                        profileTokenId
                        profileTokenAddress
                    }
                    xmtp {
                        isXMTPEnabled
                    }
                    }
                }
                }
            }
            }
            """
            poaps_data_response = None
            recommended_users = existing_users.copy()
            while True:
                if poaps_data_response is None:
                    execute_query_client = self.create_execute_query_object(
                        query=user_poaps_event_ids_query, variables={'user': address})
                    # Pagination #1: Fetch All POAPs
                    poaps_data_response = await execute_query_client.execute_paginated_query()

                if poaps_data_response.error is None:
                    event_ids = [
                        poap.get('eventId')
                        for poap in poaps_data_response.data.get('Poaps', {}).get('Poap', [])
                        if not poap.get('poapEvent', {}).get('isVirtualEvent')
                    ] if poaps_data_response.data and 'Poaps' in poaps_data_response.data and 'Poap' in poaps_data_response.data['Poaps'] else []
                    poap_holders_data_response = None
                    while True:
                        if poap_holders_data_response is None:
                            execute_query_client = self.create_execute_query_object(
                                query=poaps_by_event_ids_query, variables={'eventIds': event_ids})
                            # Pagination 2: Fetch all POAP Holders
                            poap_holders_data_response = await execute_query_client.execute_paginated_query()

                        if poap_holders_data_response.error is None:
                            recommended_users = format_poaps_data(
                                poap_holders_data_response.data.get(
                                    'Poaps', {}).get('Poap', []),
                                recommended_users
                            )

                            if not poap_holders_data_response.has_next_page:
                                break
                            else:
                                poap_holders_data_response = await poap_holders_data_response.get_next_page
                        else:
                            raise AirstackException(
                                f"Error message {poap_holders_data_response.error}")

                    if not poaps_data_response.has_next_page:
                        break
                    else:
                        poaps_data_response = await poaps_data_response.get_next_page
                else:
                    raise AirstackException(
                        f"Error message {poaps_data_response.error}")

            return recommended_users
        except Exception as e:
            error = traceback.format_exc()
            raise AirstackException(f"Error message {error}")

    async def _fetch_socials_followings(self, address: str, dapp_name: SocialsDappName = SocialsDappName.LENS, existing_users: list = []) -> list:
        """Async function to fetch all social followings of a user on Lens or Farcaster

        Args:
            address (str): user's address
            existing_users (list, optional): Existing onchain graph data. Defaults to
            None.
            dapp_name (SocialsDappName, optional): Social dapp name. Defaults to SocialsDappName.LENS.

        Returns:
            list: Concatenated list of existing onchain graph users with all social followings of a user or Lens or Farcaster
        """
        try:
            social_followings_query = """
            query MyQuery($user: Identity!, $dappName: SocialDappName!) {
            SocialFollowings(
                input: {filter: {identity: {_eq: $user}, dappName: {_eq: $dappName}}, blockchain: ALL, limit: 200}
            ) {
                Following {
                followingAddress {
                    addresses
                    domains {
                    name
                    isPrimary
                    }
                    socials {
                    dappName
                    blockchain
                    profileName
                    profileImage
                    profileTokenId
                    profileTokenAddress
                    }
                    xmtp {
                    isXMTPEnabled
                    }
                    mutualFollower: socialFollowers(
                    input: {filter: {identity: {_eq: $user}, dappName: {_eq: $dappName}}}
                    ) {
                    Follower {
                        followerAddress {
                        socials {
                            profileName
                        }
                        }
                    }
                    }
                }
                }
            }
            }
            """
            res = None
            recommended_users = existing_users.copy()
            while True:
                if res is None:
                    execute_query_client = self.create_execute_query_object(
                        query=social_followings_query, variables={'user': address, 'dappName': dapp_name})
                    res = await execute_query_client.execute_paginated_query()

                if res.error is None:
                    followings = [following['followingAddress'] for following in (res.data.get(
                        'SocialFollowings', {}).get('Following', []) or []) if 'followingAddress' in following]
                    recommended_users = format_socials_followings_data(
                        followings,
                        dapp_name,
                        recommended_users
                    )

                    if not res.has_next_page:
                        break
                    else:
                        res = await res.get_next_page
                else:
                    raise AirstackException(
                        f"Error message {res.error}")

            return recommended_users
        except Exception as e:
            error = traceback.format_exc()
            raise AirstackException(f"Error message {error}")

    async def _fetch_socials_followers(self, address: str, dapp_name: SocialsDappName = SocialsDappName.LENS, existing_users: list = []) -> list:
        """Async function to fetch all social followers of a user on Lens or Farcaster

        Args:
            address (str): user's address
            existing_users (list, optional): Existing onchain graph data. Defaults to
            None.
            dapp_name (SocialsDappName, optional): Social dapp name. Defaults to SocialsDappName.LENS.

        Returns:
            list: Concatenated list of existing onchain graph users with all social followers of a user or Lens or Farcaster
        """
        try:
            social_followers_query = """
            query MyQuery($user: Identity!, $dappName: SocialDappName!) {
            SocialFollowers(
                input: {filter: {identity: {_eq: $user}, dappName: {_eq: $dappName}}, blockchain: ALL, limit: 200}
            ) {
                Follower {
                followerAddress {
                    addresses
                    domains {
                    name
                    isPrimary
                    }
                    socials {
                    dappName
                    blockchain
                    profileName
                    profileImage
                    profileTokenId
                    profileTokenAddress
                    }
                    xmtp {
                    isXMTPEnabled
                    }
                    mutualFollowing: socialFollowings(
                    input: {filter: {identity: {_eq: $user}, dappName: {_eq: $dappName}}}
                    ) {
                    Following {
                        followingAddress {
                        socials {
                            profileName
                        }
                        }
                    }
                    }
                }
                }
            }
            }
            """
            res = None
            recommended_users = existing_users.copy()
            while True:
                if res is None:
                    execute_query_client = self.create_execute_query_object(
                        query=social_followers_query, variables={'user': address, 'dappName': dapp_name})
                    res = await execute_query_client.execute_paginated_query()

                if res.error is None:
                    followings = [following['followerAddress'] for following in (res.data.get(
                        'SocialFollowers', {}).get('Follower', []) or []) if 'followerAddress' in following]
                    recommended_users = format_socials_followers_data(
                        followings,
                        dapp_name,
                        recommended_users
                    )

                    if not res.has_next_page:
                        break
                    else:
                        res = await res.get_next_page
                else:
                    raise AirstackException(
                        f"Error message {res.error}")

            return recommended_users
        except Exception as e:
            error = traceback.format_exc()
            raise AirstackException(f"Error message {error}")

    async def _fetch_token_transfers(self, address: str, transfer_type: TransferType = TransferType.SEND, existing_users: list = []) -> list:
        """Async function to fetch all the users that interacted in token transfer with the given user on Ethereum, Polygon, or Base

        Args:
            address (str): user's address
            existing_users (list, optional): Existing onchain graph data. Defaults to
            None.
            transfer_type (TransferType, optional): Transfer type (send or received). Defaults to TransferType.SEND.

        Returns:
            list: Concatenated list of existing onchain graph users with all the users that interacted in token transfer with the given user on Ethereum, Polygon, or Base
        """
        try:
            isSend = transfer_type == TransferType.SEND
            token_sent_query = """
            query MyQuery($user: Identity!) {
            Ethereum: TokenTransfers(
                input: {filter: {from: {_eq: $user}}, blockchain: ethereum, limit: 200}
            ) {
                TokenTransfer {
                account:""" + ("from" if isSend else "to") + """{
                    addresses
                    domains {
                    name
                    isPrimary
                    }
                    socials {
                    dappName
                    blockchain
                    profileName
                    profileImage
                    profileTokenId
                    profileTokenAddress
                    }
                    xmtp {
                    isXMTPEnabled
                    }
                }
                }
            }
            Polygon: TokenTransfers(
                input: {filter: {from: {_eq: $user}}, blockchain: ethereum, limit: 200}
            ) {
                TokenTransfer {
                account:""" + ("from" if isSend else "to") + """{
                    addresses
                    domains {
                    name
                    isPrimary
                    }
                    socials {
                    dappName
                    blockchain
                    profileName
                    profileImage
                    profileTokenId
                    profileTokenAddress
                    }
                    xmtp {
                    isXMTPEnabled
                    }
                }
                }
            }
            Base: TokenTransfers(
                input: {filter: {from: {_eq: $user}}, blockchain: base, limit: 200}
            ) {
                TokenTransfer {
                account:""" + ("from" if isSend else "to") + """{
                    addresses
                    domains {
                    name
                    isPrimary
                    }
                    socials {
                    dappName
                    blockchain
                    profileName
                    profileImage
                    profileTokenId
                    profileTokenAddress
                    }
                    xmtp {
                    isXMTPEnabled
                    }
                }
                }
            }
            }
            """
            res = None
            recommended_users = existing_users.copy()
            while True:
                if res is None:
                    execute_query_client = self.create_execute_query_object(
                        query=token_sent_query, variables={'user': address})
                    res = await execute_query_client.execute_paginated_query()

                if res.error is None:
                    eth_data = [transfer['account'] for transfer in (res.data.get('Ethereum', {}).get(
                        'TokenTransfer', []) if isinstance(res.data.get('Ethereum', {}).get('TokenTransfer', []), list) else [])]
                    polygon_data = [transfer['account'] for transfer in (res.data.get('Polygon', {}).get(
                        'TokenTransfer', []) if isinstance(res.data.get('Polygon', {}).get('TokenTransfer', []), list) else [])]
                    base_data = [transfer['account'] for transfer in (res.data.get('Base', {}).get(
                        'TokenTransfer', []) if isinstance(res.data.get('Base', {}).get('TokenTransfer', []), list) else [])]
                    token_transfer = eth_data + polygon_data + base_data
                    recommended_users = (format_token_sent_data if isSend else format_token_received_data)(
                        token_transfer,
                        recommended_users
                    )

                    if not res.has_next_page:
                        break
                    else:
                        res = await res.get_next_page
                else:
                    raise AirstackException(
                        f"Error message {res.error}")

            return recommended_users
        except Exception as e:
            error = traceback.format_exc()
            raise AirstackException(f"Error message {error}")

    async def _fetch_nft_data(self, address: str, existing_users: list = [], chain: ChainType = ChainType.ETH) -> list:
        """Async function to fetch all the common NFT holders on Ethereum, Polygon, or Base

        Args:
            address (str): user's address
            existing_users (list, optional): Existing onchain graph data. Defaults to
            None.
            chain (ChainType, optional): Chain type. Defaults to ChainType.ETH.

        Returns:
            list: Concatenated list of existing onchain graph users with all the common NFT holders on Ethereum, Polygon, or Base
        """
        try:
            nft_addresses_query = """
            query MyQuery($user: Identity!, $chain: TokenBlockchain!) {
            TokenBalances(input: {filter: {tokenType: {_in: [ERC721]}, owner: {_eq: $user}}, blockchain: $chain, limit: 200}) {
                TokenBalance {
                tokenAddress
                }
            }
            }
            """

            nft_query = """
            query MyQuery($tokenAddresses: [Address!], $chain: TokenBlockchain!) {
            TokenBalances(
                input: {filter: {tokenAddress: {_in: $tokenAddresses}, tokenType: {_in: [ERC721]}}, blockchain: $chain, limit: 200}
            ) {
                TokenBalance {
                token {
                    name
                    address
                    tokenNfts {
                    tokenId
                    }
                    blockchain
                    logo {
                    small
                    }
                }
                owner {
                    addresses
                    domains {
                    name
                    isPrimary
                    }
                    socials {
                    dappName
                    blockchain
                    profileName
                    profileImage
                    profileTokenId
                    profileTokenAddress
                    }
                    xmtp {
                    isXMTPEnabled
                    }
                }
                }
            }
            }
            """

            nft_response = None
            recommended_users = existing_users.copy()
            while True:
                if nft_response is None:
                    execute_query_client = self.create_execute_query_object(
                        query=nft_addresses_query, variables={'user': address, 'chain': chain})
                    # Pagination #1: Fetch NFTs
                    nft_response = await execute_query_client.execute_paginated_query()

                if nft_response.error is None:
                    token_addresses = [token['tokenAddress'] for token in nft_response.data.get('TokenBalances', {}).get(
                        'TokenBalance', [])] if nft_response.data and 'TokenBalances' in nft_response.data and 'TokenBalance' in nft_response.data['TokenBalances'] else []
                    nft_holders_response = None
                    while True:
                        if nft_holders_response is None:
                            execute_query_client = self.create_execute_query_object(
                                query=nft_query, variables={'tokenAddresses': token_addresses, 'chain': chain})
                            # Pagination #2: Fetch NFT Holders
                            nft_holders_response = await execute_query_client.execute_paginated_query()

                        if nft_holders_response.error is None:
                            recommended_users = format_eth_nft_data(
                                nft_holders_response.data.get(
                                    'TokenBalances', {}).get('TokenBalance', []),
                                recommended_users
                            )

                            if not nft_holders_response.has_next_page:
                                break
                            else:
                                nft_holders_response = await nft_holders_response.get_next_page
                        else:
                            raise AirstackException(
                                f"Error message {nft_holders_response.error}")

                    if not nft_response.has_next_page:
                        break
                    else:
                        nft_response = await nft_response.get_next_page
                else:
                    raise AirstackException(
                        f"Error message {nft_response.error}")

            return recommended_users
        except Exception as e:
            error = traceback.format_exc()
            raise AirstackException(f"Error message {error}")

    async def fetch_onchain_graph_data(self, address: str, score_and_sort_each_response: bool = True):
        """Async function to fetch all the common NFT holders on Ethereum, Polygon, or Base

        Args:
            address (str): user's address
            existing_users (list, optional): Existing onchain graph data. Defaults to
            None.
            chain (ChainType, optional): Chain type. Defaults to ChainType.ETH.

        Returns:
            list: Concatenated list of existing onchain graph users with all the common NFT holders on Ethereum, Polygon, or Base
        """
        try:
            recommended_users = []
            fetch_functions = [
                {'fct': self._fetch_poaps_data},
                {'fct': self._fetch_socials_followings, 'args': {
                    'dapp_name': 'lens'}},
                {'fct': self._fetch_socials_followings, 'args': {
                    'dapp_name': 'farcaster'}},
                {'fct': self._fetch_socials_followers, 'args': {
                    'dapp_name': 'lens'}},
                {'fct': self._fetch_socials_followers, 'args': {
                    'dapp_name': 'farcaster'}},
                {'fct': self._fetch_token_transfers, 'args': {
                    'transfer_type': 'send'}},
                {'fct': self._fetch_token_transfers, 'args': {
                    'transfer_type': 'received'}},
                {'fct': self._fetch_nft_data, 'args': {
                    'chain': 'ethereum'}},
                {'fct': self._fetch_nft_data, 'args': {
                    'chain': 'polygon'}},
                {'fct': self._fetch_nft_data, 'args': {
                    'chain': 'base'}},
            ]
            for func in fetch_functions:
                recommended_users = await func.get('fct')(address=address, existing_users=recommended_users, **func.get('args', {}))
            return recommended_users
            # return recommended_users if score_and_sort_each_response else self._sort_by_score(self._calculate_score(recommended_users))
        except Exception:
            error = traceback.format_exc()
            raise AirstackException(f"Error message {error}")

    def _calculate_score(self, onchain_graph):
        """Calculate all user score in the onchain graph

        Args:
            onchain_graph (list): Existing onchain graph data.

        Returns:
            list: Concatenated list of existing onchain graph users with all the common NFT holders on Ethereum, Polygon, or Base
        """
        try:
            onchain_graph_users_with_score = [
                calculating_score(user) for user in onchain_graph]
            return onchain_graph_users_with_score
        except Exception as e:
            error = traceback.format_exc()
            raise AirstackException(f"Error message {error}")

    def _sort_by_score(self, recommendations):
        """Sort Onchain Graph result by the `_score` field

        Args:
            onchain_graph (list): Existing onchain graph data.

        Returns:
            list: Sorted list of onchain graph users
        """
        try:
            return sorted(recommendations, key=lambda x: x.get('_score', 0), reverse=True)
        except Exception as e:
            error = traceback.format_exc()
            raise AirstackException(f"Error message {error}")
