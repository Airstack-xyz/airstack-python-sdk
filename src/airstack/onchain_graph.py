"""
Module: onchain_graph.py
Description: This module contains the methods of Onchain Graphs.
"""

from airstack.execute_query import AirstackClient
from airstack.generic import format_poaps_data, format_farcaster_followings_data, format_lens_followings_data, format_farcaster_followers_data, format_lens_followers_data, format_token_sent_data, format_token_received_data, format_eth_nft_data, format_polygon_nft_data, calculating_score


class ExecuteOnchainGraph():
    """Class to store onchain graph function
    """

    def __init__(self, url=None, api_key=None):
        self.url = url
        self.api_client = AirstackClient(api_key=api_key)

    async def __fetch_poaps_data(self, address, existing_users=[]):
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
                execute_query_client = self.api_client.create_execute_query_object(
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
                        execute_query_client = self.api_client.create_execute_query_object(
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
                        print("Error: ", poap_holders_data_response.error)
                        break

                if not poaps_data_response.has_next_page:
                    break
                else:
                    poaps_data_response = await poaps_data_response.get_next_page
            else:
                print("Error: ", poaps_data_response.error)
                break

        return recommended_users

    async def __fetch_farcaster_followings(self, address, existing_users=[]):
        social_followings_query = """
        query MyQuery($user: Identity!) {
        SocialFollowings(
            input: {filter: {identity: {_eq: $user}, dappName: {_eq: farcaster}}, blockchain: ALL, limit: 200}
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
                input: {filter: {identity: {_eq: $user}, dappName: {_eq: farcaster}}}
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
                execute_query_client = self.api_client.create_execute_query_object(
                    query=social_followings_query, variables={'user': address})
                res = await execute_query_client.execute_paginated_query()

            if res.error is None:
                followings = [following['followingAddress'] for following in (res.data.get(
                    'SocialFollowings', {}).get('Following', []) or []) if 'followingAddress' in following]
                recommended_users = format_farcaster_followings_data(
                    followings,
                    recommended_users
                )

                if not res.has_next_page:
                    break
                else:
                    res = await res.get_next_page
            else:
                print("Error: ", res.error)
                break

        return recommended_users

    async def __fetch_lens_followings(self, address, existing_users=[]):
        social_followings_query = """
        query MyQuery($user: Identity!) {
        SocialFollowings(
            input: {filter: {identity: {_eq: $user}, dappName: {_eq: lens}}, blockchain: ALL, limit: 200}
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
                input: {filter: {identity: {_eq: $user}, dappName: {_eq: lens}}}
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
                execute_query_client = self.api_client.create_execute_query_object(
                    query=social_followings_query, variables={'user': address})
                res = await execute_query_client.execute_paginated_query()

            if res.error is None:
                followings = [following['followingAddress'] for following in (res.data.get(
                    'SocialFollowings', {}).get('Following', []) or []) if 'followingAddress' in following]
                recommended_users = format_lens_followings_data(
                    followings,
                    recommended_users
                )

                if not res.has_next_page:
                    break
                else:
                    res = await res.get_next_page
            else:
                print("Error: ", res.error)
                break

        return recommended_users

    async def __fetch_farcaster_followers(self, address, existing_users=[]):
        social_followers_query = """
        query MyQuery($user: Identity!) {
        SocialFollowers(
            input: {filter: {identity: {_eq: $user}, dappName: {_eq: farcaster}}, blockchain: ALL, limit: 200}
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
                input: {filter: {identity: {_eq: $user}, dappName: {_eq: farcaster}}}
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
                execute_query_client = self.api_client.create_execute_query_object(
                    query=social_followers_query, variables={'user': address})
                res = await execute_query_client.execute_paginated_query()

            if res.error is None:
                followings = [following['followerAddress'] for following in (res.data.get(
                    'SocialFollowers', {}).get('Follower', []) or []) if 'followerAddress' in following]
                recommended_users = format_farcaster_followers_data(
                    followings,
                    recommended_users
                )

                if not res.has_next_page:
                    break
                else:
                    res = await res.get_next_page
            else:
                print("Error: ", res.error)
                break

        return recommended_users

    async def __fetch_lens_followers(self, address, existing_users=[]):
        social_followings_query = """
        query MyQuery($user: Identity!) {
        SocialFollowings(
            input: {filter: {identity: {_eq: $user}, dappName: {_eq: lens}}, blockchain: ALL, limit: 200}
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
                input: {filter: {identity: {_eq: $user}, dappName: {_eq: lens}}}
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
                execute_query_client = self.api_client.create_execute_query_object(
                    query=social_followings_query, variables={'user': address})
                res = await execute_query_client.execute_paginated_query()

            if res.error is None:
                followings = [following['followingAddress'] for following in (res.data.get(
                    'SocialFollowings', {}).get('Following', []) or []) if 'followingAddress' in following]
                recommended_users = format_lens_followings_data(
                    followings,
                    recommended_users
                )

                if not res.has_next_page:
                    break
                else:
                    res = await res.get_next_page
            else:
                print("Error: ", res.error)
                break

        return recommended_users

    async def __fetch_token_sent(self, address, existing_users=[]):
        token_sent_query = """
        query MyQuery($user: Identity!) {
        Ethereum: TokenTransfers(
            input: {filter: {from: {_eq: $user}}, blockchain: ethereum, limit: 200}
        ) {
            TokenTransfer {
            account: from {
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
            account: from {
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
                execute_query_client = self.api_client.create_execute_query_object(
                    query=token_sent_query, variables={'user': address})
                res = await execute_query_client.execute_paginated_query()

            if res.error is None:
                eth_data = [transfer['account'] for transfer in (res.data.get('Ethereum', {}).get(
                    'TokenTransfer', []) if res.data and 'Ethereum' in res.data and 'TokenTransfer' in res.data['Ethereum'] else [])]
                polygon_data = [transfer['account'] for transfer in (res.data.get('Polygon', {}).get(
                    'TokenTransfer', []) if res.data and 'Polygon' in res.data and 'TokenTransfer' in res.data['Polygon'] else [])]
                token_transfer = eth_data + polygon_data
                recommended_users = format_token_sent_data(
                    token_transfer,
                    recommended_users
                )

                if not res.has_next_page:
                    break
                else:
                    res = await res.get_next_page
            else:
                print("Error: ", res.error)
                break

        return recommended_users

    async def __fetch_token_received(self, address, existing_users=[]):
        token_received_query = """
        query MyQuery($user: Identity!) {
        Ethereum: TokenTransfers(
            input: {filter: {to: {_eq: $user}}, blockchain: ethereum, limit: 200}
        ) {
            TokenTransfer {
            account: to {
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
            input: {filter: {to: {_eq: $user}}, blockchain: ethereum, limit: 200}
        ) {
            TokenTransfer {
            account: to {
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
                execute_query_client = self.api_client.create_execute_query_object(
                    query=token_received_query, variables={'user': address})
                res = await execute_query_client.execute_paginated_query()

            if res.error is None:
                eth_data = [transfer['account'] for transfer in (res.data.get('Ethereum', {}).get(
                    'TokenTransfer', []) if res.data and 'Ethereum' in res.data and 'TokenTransfer' in res.data['Ethereum'] else [])]
                polygon_data = [transfer['account'] for transfer in (res.data.get('Polygon', {}).get(
                    'TokenTransfer', []) if res.data and 'Polygon' in res.data and 'TokenTransfer' in res.data['Polygon'] else [])]
                token_transfer = eth_data + polygon_data
                recommended_users = format_token_received_data(
                    token_transfer,
                    recommended_users
                )

                if not res.has_next_page:
                    break
                else:
                    res = await res.get_next_page
            else:
                print("Error: ", res.error)
                break

        return recommended_users

    async def __fetch_eth_nft(self, address, existing_users=[]):
        nft_addresses_query = """
        query MyQuery($user: Identity!) {
        TokenBalances(input: {filter: {tokenType: {_in: [ERC721]}, owner: {_eq: $user}}, blockchain: ethereum, limit: 200}) {
            TokenBalance {
            tokenAddress
            }
        }
        }
        """

        nft_query = """
        query MyQuery($tokenAddresses: [Address!]) {
        TokenBalances(
            input: {filter: {tokenAddress: {_in: $tokenAddresses}, tokenType: {_in: [ERC721]}}, blockchain: ethereum, limit: 200}
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

        eth_nft_response = None
        recommended_users = existing_users.copy()
        while True:
            if eth_nft_response is None:
                execute_query_client = self.api_client.create_execute_query_object(
                    query=nft_addresses_query, variables={'user': address})
                # Pagination #1: Fetch Ethereum NFTs
                eth_nft_response = await execute_query_client.execute_paginated_query()

            if eth_nft_response.error is None:
                token_addresses = [token['tokenAddress'] for token in eth_nft_response.data.get('TokenBalances', {}).get(
                    'TokenBalance', [])] if eth_nft_response.data and 'TokenBalances' in eth_nft_response.data and 'TokenBalance' in eth_nft_response.data['TokenBalances'] else []
                eth_nft_holders_response = None
                while True:
                    if eth_nft_holders_response is None:
                        execute_query_client = self.api_client.create_execute_query_object(
                            query=nft_query, variables={'tokenAddresses': token_addresses})
                        # Pagination #2: Fetch Ethereum NFT Holders
                        eth_nft_holders_response = await execute_query_client.execute_paginated_query()

                    if eth_nft_holders_response.error is None:
                        recommended_users = format_eth_nft_data(
                            eth_nft_holders_response.data.get(
                                'TokenBalances', {}).get('TokenBalance', []),
                            recommended_users
                        )

                        if not eth_nft_holders_response.has_next_page:
                            break
                        else:
                            eth_nft_holders_response = await eth_nft_holders_response.get_next_page
                    else:
                        print("Error: ", eth_nft_holders_response.error)
                        break

                if not eth_nft_response.has_next_page:
                    break
                else:
                    eth_nft_response = await eth_nft_response.get_next_page
            else:
                print("Error: ", eth_nft_response.error)
                break

        return recommended_users

    async def __fetch_polygon_nft(self, address, existing_users=[]):
        nft_addresses_query = """
        query MyQuery($user: Identity!) {
        TokenBalances(input: {filter: {tokenType: {_in: [ERC721]}, owner: {_eq: $user}}, blockchain: polygon, limit: 200}) {
            TokenBalance {
            tokenAddress
            }
        }
        }
        """

        nft_query = """
        query MyQuery($tokenAddresses: [Address!]) {
        TokenBalances(
            input: {filter: {tokenAddress: {_in: $tokenAddresses}, tokenType: {_in: [ERC721]}}, blockchain: polygon, limit: 200}
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
        polygon_nft_response = None
        recommended_users = existing_users.copy()
        while True:
            if polygon_nft_response is None:
                execute_query_client = self.api_client.create_execute_query_object(
                    query=nft_addresses_query, variables={'user': address})
                # Pagination #1: Fetch Polygon NFTs
                polygon_nft_response = await execute_query_client.execute_paginated_query()

            if polygon_nft_response.error is None:
                token_addresses = [token['tokenAddress'] for token in polygon_nft_response.data.get('TokenBalances', {}).get(
                    'TokenBalance', [])] if polygon_nft_response.data and 'TokenBalances' in polygon_nft_response.data and 'TokenBalance' in polygon_nft_response.data['TokenBalances'] else []
                polygon_nft_holders_response = None
                while True:
                    if polygon_nft_holders_response is None:
                        execute_query_client = self.api_client.create_execute_query_object(
                            query=nft_query, variables={'tokenAddresses': token_addresses})
                        # Pagination #2: Fetch Polygon NFT Holders
                        polygon_nft_holders_response = await execute_query_client.execute_paginated_query()

                    if polygon_nft_holders_response.error is None:
                        recommended_users = format_polygon_nft_data(
                            polygon_nft_holders_response.data.get(
                                'TokenBalances', {}).get('TokenBalance', []),
                            recommended_users
                        )

                        if not polygon_nft_holders_response.has_next_page:
                            break
                        else:
                            polygon_nft_holders_response = await polygon_nft_holders_response.get_next_page
                    else:
                        print("Error: ", polygon_nft_holders_response.error)
                        break

                if not polygon_nft_response.has_next_page:
                    break
                else:
                    polygon_nft_response = await polygon_nft_response.get_next_page
            else:
                print("Error: ", polygon_nft_response.error)
                break

        return recommended_users

    async def fetch_onchain_graph_data(self, address):
        recommended_users = []
        fetch_functions = [
            self.__fetch_poaps_data,
            self.__fetch_farcaster_followings,
            self.__fetch_lens_followings,
            self.__fetch_farcaster_followers,
            self.__fetch_lens_followers,
            self.__fetch_token_sent,
            self.__fetch_token_received,
            self.__fetch_eth_nft,
            self.__fetch_polygon_nft,
        ]
        for func in fetch_functions:
            recommended_users = await func(address, recommended_users)
        return recommended_users

    def calculate_score(self, onchain_graph):
        onchain_graph_users_with_score = [
            calculating_score(user) for user in onchain_graph]
        return onchain_graph_users_with_score

    def sort_by_score(self, recommendations):
        return sorted(recommendations, key=lambda x: x.get('_score', 0), reverse=True)
