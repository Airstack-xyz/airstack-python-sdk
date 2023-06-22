# airstack-python-sdk

The Airstack Python SDK is a library that allows Python developers to integrate Airstack's blockchain functionalities into their applications. With this SDK, developers can perform various tasks, such as querying and fetching data from smart contracts, displaying NFT assets.

# Installation

`pip3 install airstack`

# Getting started
To use the SDK you will need airstack api-key, which you can find in your profile setting section in airstack web, once you have it you can initialise the Airstackclient with the api-key.
```python
from airstack.execute_query import AirstackClient

api_client = AirstackClient(api_key='api-key')

```

# Methods
## execute_query
The execute query method query the data and return the data in asynchronous, it returns query_response which has below data
- `query_response.data`: data returned by the query
- `query_response.status_code`: status code of the query response
- `query_response.error`: any error that occurred while loading the query

### Example
```python
import asyncio
from airstack.execute_query import AirstackClient

api_client = AirstackClient(api_key='api-key')

# Replace the below query and variables to match your use case 
query = """
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

variables = {
        "name1": "0x1130547436810db920fa73681c946fea15e9b758",
        "name2": "0xf4eced2f682ce333f96f2d8966c613ded8fc95dd",
}

# Create a Query object
execute_query_client = api_client.create_execute_query_object(query=query, variables=variables)

async def get_token_balances():
    # Execute the query and return its results
    results = await execute_query_client.execute_query()
    return results


query_response = asyncio.run(get_token_balances())
```

## execute_paginated_query
**Note:** pagination methods only works with queries that has support for pagination, and the query passed to method must have a cursor as argument for it to work.

The `execute_paginated_query` method provides a simple way to paginate the data returned by a query. It works the same as the `execute_query` method, it returns query_response which has below data:

- `query_response.data`: data returned by the query
- `query_response.status_code`: status code of the query response
- `query_response.error`: any error that occurred while loading the query
- `query_response.has_next_page`: a boolean indicating whether there is another page of data after the current page
- `query_response.has_prev_page`: a boolean indicating whether there is another page of data before the current page
- `query_response.get_next_page`: a function that can be called to fetch the next page of data
- `query_response.get_prev_page`: a function that can be called to fetch the previous page of data

### Example 1
```python
import asyncio
from airstack.execute_query import AirstackClient

api_client = AirstackClient(api_key='api-key')

# Replace the below query and variables to match your use case 
query = """
        query CurrentTokenBalances($identity: Identity) {
        Ethereum: TokenBalances(
            input: {filter: {owner: {_eq: $identity}}, blockchain: ethereum, order: {lastUpdatedTimestamp: DESC}, limit: 200}
        ) {
            TokenBalance {
            amount
            tokenType
            tokenAddress
            token {
                name
            }
            }
            pageInfo {
            nextCursor
            prevCursor
            }
        }
        Polygon: TokenBalances(
            input: {filter: {owner: {_eq: $identity}}, blockchain: polygon, order: {lastUpdatedTimestamp: DESC}, limit: 200}
        ) {
            TokenBalance {
            amount
            tokenType
            tokenAddress
            token {
                name
            }
            }
            pageInfo {
            nextCursor
            prevCursor
            }
        }
        }
        """

variables = {
  "identity": "vitalik.eth"
}

# Create a Query object
execute_query_client = api_client.create_execute_query_object(query=query, variables=variables)

async def get_token_balances():
    # Execute the paginated query
    query_response = await execute_query_client.execute_paginated_query()

    # Iteratively, fetch the results from next pages
    while query_response.has_next_page:
        yield query_response
        query_response = await query_response.get_next_page
    
    yield query_response


async def get_all_pages():
    responses = get_token_balances()
    async for response in responses:
        if not response.error: print(response.data)

asyncio.run(get_all_pages()) 
```

Example 2: 
```
```python
import asyncio
from airstack.execute_query import AirstackClient

api_client = AirstackClient(api_key='api-key')

# Use the query and variables from previous example

# Create a Query object
execute_query_client = api_client.create_execute_query_object(query=query, variables=variables)

async def get_first_page():
    query_response = await execute_query_client.execute_paginated_query()
    
    if query_response.has_next_page:
        query_response = await query_response.get_next_page
    
    if query_response.has_prev_page:
        query_response = await query_response.get_prev_page
    
    yield query_response


async def show_usage_next_prev():
    async for first_page in get_first_page():
        if not first_page.error:
            print(first_page.data)

asyncio.run(show_usage_next_prev())
```