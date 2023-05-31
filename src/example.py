import asyncio
from airstack.execute_query import AirstackClient


async def main():
    api_client = AirstackClient(api_key='api_key')

    query1 = """
 query MyQuery($name1: Address!, $name2: Address!) {
  TokenBalances(
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
  test2: TokenTransfers(
    input: {filter: {tokenAddress: {_eq: $name2}}, blockchain: ethereum}
  ) {
    pageInfo {
      nextCursor
      prevCursor
    }
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

    query_response = await api_client.execute_paginated_query(
        query=query1, variables=variables1)

    if query_response.has_next_page:
        next_page_response = await query_response.get_next_page()
    if next_page_response.has_prev_page:
        pev_page_response = await query_response.get_prev_page()

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
        print(f"Response: {query_response.response}")

    query_response = await api_client.execute_query(query=query, variables=variables)

    # Process the next page response
    if query_response.error:
        print(f"Error: {query_response.error}")
    else:
        print(f"Response: {query_response.response}")


asyncio.run(main())
