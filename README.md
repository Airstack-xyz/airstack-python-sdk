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
from airstack.execute_query import AirstackClient

api_client = AirstackClient(api_key='api-key')

execute_query_client = api_client.create_execute_query_object(query=query, variables=variables)

query_response = await execute_query_client.execute_query()
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

### Example
```python
from airstack.execute_query import AirstackClient

api_client = AirstackClient(api_key='api-key')

execute_query_client = api_client.create_execute_query_object(query=query, variables=variables)

query_response = await execute_query_client.execute_paginated_query()

if query_response.has_next_page:
    next_page_response = await query_response.get_next_page

if next_page_response.has_prev_page:
    prev_page_response = await query_response.get_prev_page
```


