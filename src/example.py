import asyncio
from airstack.execute_query import AirstackClient


async def main():
    api_client = AirstackClient(api_key='api_key')

    query1 = """
 query MyQuery($name1: Address!, $name2: Address!) {
  TokenBalances(
    input: {filter: {tokenAddress: {_eq: $name1}}, blockchain: ethereum}
  ) {
    TokenBalance {
      chainId
      blockchain
      amount
      lastUpdatedTimestamp
      id
    }
  }
  test2: TokenTransfers(
    input: {filter: {tokenAddress: {_eq: $name2}}, blockchain: ethereum}
  ) {
    TokenTransfer {
      chainId
      blockchain
      id
      amount
    }
  }
}
  """
    variables1 = {
        "name1": "0x1130547436810db920fa73681c946fea15e9b758",
        "name2": "0xf4eced2f682ce333f96f2d8966c613ded8fc95dd",
    }

    execute_query_client = api_client.create_execute_query_object(query=query1, variables=variables1)
    query_response = await execute_query_client.execute_paginated_query()
    if query_response.has_next_page:
        next_page_response = await query_response.get_next_page
    if next_page_response.has_prev_page:
        prev_page_response = await next_page_response.get_prev_page
    
    query = """
     query MyQuery($name1: Address!) {
      test1: TokenBalances(
        input: {filter: {tokenAddress: {_eq: $name1}}, blockchain: ethereum}
      ) {
        pageInfo {
          nextCursor
          prevCursor
        }
        TokenBalance {
          chainId
          blockchain
          amount
          lastUpdatedTimestamp
          id
        }
      }
    }
      """
    variables = {
        "name1": "0x1130547436810db920fa73681c946fea15e9b758",
    }

    # Process the next page response
    if query_response.error:
        print(f"Error: {query_response.error}")
    else:
        print(f"Response: {query_response.data}")
    
    execute_query_client = api_client.create_execute_query_object(query=query, variables=variables)
    query_response = await execute_query_client.execute_query()

    # Process the next page response
    if query_response.error:
        print(f"Error: {query_response.error}")
    else:
        print(f"Response: {query_response.data}")


  # Example to use popular queries

    execute_query_client = api_client.create_popular_queries_object()

    query_response = await execute_query_client.get_all_tokens(variables={
      "identity": "vitalik.eth",
      "tokenType": "ERC721",
      "blockchain": "ethereum",
      "limit": 20
    })

    query_response = await execute_query_client.get_token_details(variables={
    "address": "0x9340204616750cb61e56437befc95172c6ff6606",
      "blockchain": "ethereum"
    })

    query_response = await execute_query_client.get_nft_details(variables={
    "address": "0x9340204616750cb61e56437befc95172c6ff6606",
  "blockchain": "ethereum",
  "tokenId": "2"
    })

    query_response = await execute_query_client.get_all_nfts(variables={
   "address": "0x9340204616750cb61e56437befc95172c6ff6606",
  "blockchain": "ethereum",
  "limit": 40
    })

    query_response = await execute_query_client.get_nft_image(variables={
    "address": "0x9340204616750cb61e56437befc95172c6ff6606",
  "blockchain": "ethereum",
  "tokenId": "2"
    })

    query_response = await execute_query_client.get_wallet_social_and_ens(variables={
    "identity": "betashop.eth",
  "blockchain": "ethereum"
    })

    query_response = await execute_query_client.get_wallet_ens(variables={
    "identity": "betashop.eth",
  "blockchain": "ethereum"
    })

    query_response = await execute_query_client.get_wallet_balance_for_token(variables={
    "owner": "",
  "blockchain": "ethereum",
  "tokenAddress": "0x9340204616750cb61e56437befc95172c6ff6606"
    })

    query_response = await execute_query_client.get_token_collection_owner(variables={
    "tokenAddress": "0x9340204616750cb61e56437befc95172c6ff6606",
  "blockchain": "ethereum",
  "limit": 30
    })

    query_response = await execute_query_client.get_nft_owners(variables={
    "tokenAddress": "0x9340204616750cb61e56437befc95172c6ff6606",
  "blockchain": "ethereum",
  "tokenId": "1"
    })

    query_response = await execute_query_client.get_primary_domain(variables={
   "identity": "betashop.eth",
  "blockchain": "ethereum"
    })

    query_response = await execute_query_client.get_subdomains(variables={
   "owner": "betashop.eth",
  "blockchain": "ethereum"
    })

    query_response = await execute_query_client.get_token_transfers(variables={
   "tokenAddress": "0x32e14d6f3dda2b95e505b14eb4552fd3eeaa1f0d",
  "blockchain": "ethereum",
  "limit": 30
    })

    query_response = await execute_query_client.get_nft_transfers(variables={
      "tokenId": "1053",
   "tokenAddress": "0x32e14d6f3dda2b95e505b14eb4552fd3eeaa1f0d",
  "blockchain": "ethereum",
  "limit": 30
    })

asyncio.run(main())
