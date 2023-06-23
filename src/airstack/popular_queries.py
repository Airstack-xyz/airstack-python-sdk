"""
Module: popular_queries.py
Description: This module contains the methods of popular queries.
"""

from airstack.execute_query import AirstackClient

class ExecutePopularQueries():
    """Class to store popular queries function
    """

    def __init__(self, url=None, api_key=None, timeout=None):
        """Init function for popular queries

        Args:
            url (str, optional): base url for server. Defaults to None.
            api_key (str, required): api key. Defaults to None.

        """
        self.url = url
        self.timeout = timeout
        self.api_key = api_key

    async def get_token_balances(self, variables):
        """Func to get all tokens

        Args:
            variables (dict): Variables required for the query.
            - identity (Identity): The wallet address identity.
            - tokenType (list): List of token types.
            - blockchain (TokenBlockchain): The blockchain type.
            - limit (int): The limit of items to retrieve.
        """
        _query = """
            query GetTokensHeldByWalletAddress($identity: Identity, $tokenType: [TokenType!], $blockchain: TokenBlockchain!, $limit: Int) {
                TokenBalances(
                    input: {filter: {owner: {_eq: $identity}, tokenType: {_in: $tokenType}}, blockchain: $blockchain, limit: $limit}
                ) {
                    TokenBalance {
                    amount
                    formattedAmount
                    blockchain
                    tokenAddress
                    tokenId
                    token {
                        name
                        symbol
                        decimals
                        totalSupply
                        baseURI
                        contractMetaData {
                        description
                        image
                        name
                        }
                        logo {
                        large
                        medium
                        original
                        small
                        }
                        projectDetails {
                        collectionName
                        description
                        imageUrl
                        }
                    }
                    tokenNfts {
                        metaData {
                        animationUrl
                        backgroundColor
                        description
                        externalUrl
                        image
                        name
                        youtubeUrl
                        imageData
                        }
                        tokenURI
                    }
                    tokenType
                    }
                    pageInfo {
                    nextCursor
                    prevCursor
                    }
                }
            }
        """
        execute_query_object = AirstackClient.create_execute_query_object(self,
        query=_query, variables=variables)
        return await execute_query_object.execute_paginated_query()

    async def get_token_details(self, variables):
        """Func to get token details for given contract address

        Args:
            variables (dict): Variables required for the query.
            - address (Address): Token address.
            - blockchain (TokenBlockchain): The blockchain type.
        """
        _query = """
            query TokenDetails($address: Address!, $blockchain: TokenBlockchain!) {
                Token(input: {address: $address, blockchain: $blockchain}) {
                    name
                    symbol
                    decimals
                    totalSupply
                    type
                    baseURI
                    address
                    blockchain
                    logo {
                    large
                    medium
                    original
                    small
                    }
                    projectDetails {
                    collectionName
                    description
                    imageUrl
                    discordUrl
                    externalUrl
                    twitterUrl
                    }
                }
            }
        """
        execute_query_object = AirstackClient.create_execute_query_object(self,
        query=_query, variables=variables)
        return await execute_query_object.execute_query()

    async def get_nft_details(self, variables):
        """Func to get nft details for a given contract address and tokenId

        Args:
            variables (dict): Variables required for the query.
            - address (Address): Nft token address.
            - tokenId (String): tokenId.
            - blockchain (TokenBlockchain): The blockchain type.
        """
        _query = """
            query GetNFTDetails($address: Address!, $tokenId: String!, $blockchain: TokenBlockchain!) {
                TokenNft(input: {address: $address, tokenId: $tokenId, blockchain: $blockchain}) {
                    address
                    blockchain
                    contentType
                    contentValue {
                    audio
                    animation_url {
                        original
                    }
                    image {
                        extraSmall
                        medium
                        large
                        original
                        small
                    }
                    video
                    }
                    metaData {
                    animationUrl
                    backgroundColor
                    attributes {
                        displayType
                        maxValue
                        value
                        trait_type
                    }
                    description
                    externalUrl
                    image
                    imageData
                    youtubeUrl
                    name
                    }
                    tokenURI
                    type
                    tokenId
                    token {
                    baseURI
                    address
                    blockchain
                    contractMetaData {
                        description
                        image
                        name
                    }
                    decimals
                    logo {
                        large
                        medium
                        small
                        original
                    }
                    name
                    projectDetails {
                        collectionName
                        description
                        imageUrl
                    }
                    symbol
                    totalSupply
                    type
                    }
                }
            }
        """
        execute_query_object = AirstackClient.create_execute_query_object(self,
        query=_query, variables=variables)
        return await execute_query_object.execute_query()

    async def get_nfts(self, variables):
        """Func to get all nfts of a collection

        Args:
            variables (dict): Variables required for the query.
            - address (Address): Nft token address.
            - blockchain (TokenBlockchain): The blockchain type.
            - limit (int): The limit of items to retrieve.
        """
        _query = """
            query GetAllNFTs($address: Address!, $blockchain: TokenBlockchain!, $limit: Int) {
                TokenNfts(
                    input: {blockchain: $blockchain, limit: $limit, filter: {address: {_eq: $address}}}
                ) {
                    TokenNft {
                    address
                    blockchain
                    contentType
                    contentValue {
                        audio
                        animation_url {
                        original
                        }
                        image {
                        extraSmall
                        medium
                        large
                        original
                        small
                        }
                        video
                    }
                    metaData {
                        animationUrl
                        backgroundColor
                        attributes {
                        displayType
                        maxValue
                        value
                        trait_type
                        }
                        description
                        externalUrl
                        image
                        imageData
                        youtubeUrl
                        name
                    }
                    tokenURI
                    type
                    tokenId
                    }
                    pageInfo {
                    nextCursor
                    prevCursor
                    }
                }
            }
        """
        execute_query_object = AirstackClient.create_execute_query_object(self,
        query=_query, variables=variables)
        return await execute_query_object.execute_paginated_query()

    async def get_nft_images(self, variables):
        """Func to get image of a nft

        Args:
            variables (dict): Variables required for the query.
            - address (Address): Nft token address.
            - tokenId (String): tokenId.
            - blockchain (TokenBlockchain): The blockchain type.
        """
        _query = """
            query GetImageOfNFT($address: Address!, $tokenId: String!, $blockchain: TokenBlockchain!) {
                TokenNft(input: {address: $address, tokenId: $tokenId, blockchain: $blockchain}) {
                    contentValue {
                    image {
                        original
                        extraSmall
                        large
                        medium
                        small
                    }
                    }
                }
            }
        """
        execute_query_object = AirstackClient.create_execute_query_object(self,
        query=_query, variables=variables)
        return await execute_query_object.execute_query()

    async def get_wallet_ens_and_social(self, variables):
        """Func to get all social profile and ENS name of an wallet

        Args:
            variables (dict): Variables required for the query.
            - identity (Identity): The wallet address identity.
            - blockchain (TokenBlockchain): The blockchain type.
        """
        _query = """
            query GetSocialProfileAndENS($identity: Identity!, $blockchain: TokenBlockchain!) {
                Wallet(input: {identity: $identity, blockchain: $blockchain}) {
                    domains {
                    dappName
                    owner
                    isPrimary
                    }
                    socials {
                    dappName
                    profileName
                    profileTokenAddress
                    profileTokenId
                    userId
                    chainId
                    blockchain
                    }
                }
            }
        """
        execute_query_object = AirstackClient.create_execute_query_object(self,
        query=_query, variables=variables)
        return await execute_query_object.execute_query()

    async def get_wallet_ens(self, variables):
        """Func to get the ENS name of an wallet address

        Args:
            variables (dict): Variables required for the query.
            - identity (Identity): The wallet address identity.
            - blockchain (TokenBlockchain): The blockchain type.
        """
        _query = """
            query GetENSName($identity: Identity!, $blockchain: TokenBlockchain!) {
                Wallet(input: {identity: $identity, blockchain: $blockchain}) {
                    primaryDomain {
                    name
                    dappName
                    }
                    domains {
                    name
                    owner
                    parent
                    subDomainCount
                    subDomains {
                        name
                        owner
                        parent
                    }
                    tokenId
                    blockchain
                    dappName
                    resolvedAddress
                    isPrimary
                    expiryTimestamp
                    }
                }
            }
        """
        execute_query_object = AirstackClient.create_execute_query_object(self,
        query=_query, variables=variables)
        return await execute_query_object.execute_query()

    async def get_balance_of_token(self, variables):
        """Func to get balance of wallet address for a particular token

        Args:
            variables (dict): Variables required for the query.
            - blockchain (TokenBlockchain): The blockchain type.
            - tokenAddress (Address): Token address.
            - owner (Identity): The wallet address identity.
        """
        _query = """
            query GetBalance($blockchain: TokenBlockchain!, $tokenAddress: Address!, $owner: Identity) {
                TokenBalance(
                    input: {blockchain: $blockchain, tokenAddress: $tokenAddress, owner: $owner}
                ) {
                    amount
                    formattedAmount
                    tokenType
                    tokenId
                    token {
                    name
                    symbol
                    decimals
                    totalSupply
                    }
                    tokenNfts {
                    contentType
                    contentValue {
                        image {
                        extraSmall
                        large
                        medium
                        original
                        small
                        }
                        animation_url {
                        original
                        }
                        audio
                        video
                    }
                    metaData {
                        animationUrl
                        attributes {
                        displayType
                        maxValue
                        trait_type
                        value
                        }
                        backgroundColor
                        description
                        externalUrl
                        image
                        imageData
                        name
                        youtubeUrl
                    }
                    tokenURI
                    tokenId
                    }
                }
            }
        """
        execute_query_object = AirstackClient.create_execute_query_object(self,
        query=_query, variables=variables)
        return await execute_query_object.execute_query()

    async def get_holders_of_collection(self, variables):
        """Func to get owners of a token collection

        Args:
            variables (dict): Variables required for the query.
            - tokenAddress (Address): Token address.
            - blockchain (TokenBlockchain): The blockchain type.
            - limit (int): The limit of items to retrieve.
        """
        _query = """
            query GetOwners($tokenAddress: Address, $blockchain: TokenBlockchain!, $limit: Int) {
                TokenBalances(
                    input: {filter: {tokenAddress: {_eq: $tokenAddress}}, blockchain: $blockchain, limit: $limit}
                ) {
                    TokenBalance {
                    token {
                        name
                        symbol
                        decimals
                    }
                    tokenId
                    tokenType
                    tokenNfts {
                        contentType
                        contentValue {
                        animation_url {
                            original
                        }
                        audio
                        image {
                            extraSmall
                            large
                            medium
                            original
                            small
                        }
                        video
                        }
                    }
                    owner {
                        addresses
                        primaryDomain {
                        name
                        resolvedAddress
                        }
                        domains {
                        name
                        owner
                        }
                        socials {
                        dappName
                        profileName
                        userAddress
                        userAssociatedAddresses
                        }
                    }
                    }
                    pageInfo {
                    nextCursor
                    prevCursor
                    }
                }
            }
        """
        execute_query_object = AirstackClient.create_execute_query_object(self,
        query=_query, variables=variables)
        return await execute_query_object.execute_paginated_query()

    async def get_holders_of_nft(self, variables):
        """Func to get owner(s) of the NFT

        Args:
            variables (dict): Variables required for the query.
            - tokenAddress (Address): Token address.
            - tokenId (String): tokenId.
            - blockchain (TokenBlockchain): The blockchain type.
        """
        _query = """
            query GetOwners($tokenAddress: Address, $tokenId: String, $blockchain: TokenBlockchain!) {
                TokenBalances(
                    input: {filter: {tokenAddress: {_eq: $tokenAddress}, tokenId: {_eq: $tokenId}}, blockchain: $blockchain}
                ) {
                    TokenBalance {
                    token {
                        name
                        symbol
                        decimals
                    }
                    tokenId
                    tokenType
                    tokenNfts {
                        contentType
                        contentValue {
                        animation_url {
                            original
                        }
                        audio
                        image {
                            extraSmall
                            large
                            medium
                            original
                            small
                        }
                        video
                        }
                    }
                    owner {
                        addresses
                        primaryDomain {
                        name
                        resolvedAddress
                        }
                        domains {
                        name
                        owner
                        }
                        socials {
                        dappName
                        profileName
                        userAddress
                        userAssociatedAddresses
                        }
                    }
                    }
                    pageInfo {
                    nextCursor
                    prevCursor
                    }
                }
            }
        """
        execute_query_object = AirstackClient.create_execute_query_object(self,
        query=_query, variables=variables)
        return await execute_query_object.execute_paginated_query()

    async def get_primary_ens(self, variables):
        """Func to get Primary Domain for an address

        Args:
            variables (dict): Variables required for the query.
            - identity (Identity): The wallet address identity.
            - blockchain (TokenBlockchain): The blockchain type.
        """
        _query = """
            query GetPrimaryDomain($identity: Identity!, $blockchain: TokenBlockchain!) {
                Wallet(input: {identity: $identity, blockchain: $blockchain}) {
                    primaryDomain {
                    name
                    dappName
                    tokenId
                    chainId
                    blockchain
                    labelName
                    labelHash
                    owner
                    parent
                    }
                }
            }
        """
        execute_query_object = AirstackClient.create_execute_query_object(self,
        query=_query, variables=variables)
        return await execute_query_object.execute_query()

    async def get_ens_subdomains(self, variables):
        """Func to get sub domains for an address

        Args:
            variables (dict): Variables required for the query.
            - owner (Identity): domain owner.
            - blockchain (TokenBlockchain): The blockchain type.
        """
        _query = """
            query GetSubDomains($owner: Identity, $blockchain: Blockchain!) {
                Domains(input: {filter: {owner: {_eq: $owner}}, blockchain: $blockchain}) {
                    Domain {
                    subDomains {
                        name
                        dappName
                        tokenId
                        chainId
                        blockchain
                        labelName
                        labelHash
                        owner
                        parent
                        expiryTimestamp
                        resolvedAddress
                    }
                    name
                    dappName
                    tokenId
                    chainId
                    blockchain
                    labelName
                    labelHash
                    owner
                    parent
                    }
                    pageInfo {
                    nextCursor
                    prevCursor
                    }
                }
            }
        """
        execute_query_object = AirstackClient.create_execute_query_object(self,
        query=_query, variables=variables)
        return await execute_query_object.execute_paginated_query()

    async def get_token_transfers(self, variables):
        """Func to get all transfer of a token

        Args:
            variables (dict): Variables required for the query.
            - tokenAddress (Address): Token address.
            - blockchain (TokenBlockchain): The blockchain type.
            - limit (int): The limit of items to retrieve.
        """
        _query = """
            query GetAllTransfersOfToken($tokenAddress: Address, $blockchain: TokenBlockchain!, $limit: Int) {
                TokenTransfers(
                    input: {filter: { tokenAddress: {_eq: $tokenAddress}}, blockchain: $blockchain, limit: $limit}
                ) {
                    TokenTransfer {
                    amount
                    blockNumber
                    blockTimestamp
                    from {
                        addresses
                    }
                    to {
                        addresses
                    }
                    tokenAddress
                    transactionHash
                    tokenId
                    tokenType
                    blockchain
                    }
                    pageInfo {
                    nextCursor
                    prevCursor
                    }
                }
            }
        """
        execute_query_object = AirstackClient.create_execute_query_object(self,
        query=_query, variables=variables)
        return await execute_query_object.execute_paginated_query()

    async def get_nft_transfers(self, variables):
        """Func to get all transfer of a token NFT

        Args:
            variables (dict): Variables required for the query.
            - tokenAddress (Address): Token address.
            - tokenId (String): tokenId.
            - blockchain (TokenBlockchain): The blockchain type.
            - limit (int): The limit of items to retrieve.
        """
        _query = """
            query GetAllTransfersOfTokenNFT($tokenAddress: Address, $tokenId: String, $blockchain: TokenBlockchain!, $limit: Int) {
                TokenTransfers(
                    input: {filter: {tokenId: {_eq: $tokenId}, tokenAddress: {_eq: $tokenAddress}}, blockchain: $blockchain, limit: $limit}
                ) {
                    TokenTransfer {
                    amount
                    blockNumber
                    blockTimestamp
                    from {
                        addresses
                    }
                    to {
                        addresses
                    }
                    tokenAddress
                    transactionHash
                    tokenId
                    tokenType
                    blockchain
                    }
                    pageInfo {
                    nextCursor
                    prevCursor
                    }
                }
            }
        """
        execute_query_object = AirstackClient.create_execute_query_object(self,
        query=_query, variables=variables)
        return await execute_query_object.execute_paginated_query()
