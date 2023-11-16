import asyncio
from airstack.execute_query import AirstackClient


async def main():
    api_client = AirstackClient(api_key='ef3d1cdeafb642d3a8d6a44664ce566c')
    onchain_graph_client = api_client.onchain_graph()
    res = await onchain_graph_client.fetch_onchain_graph_data("betashop.eth")
    res_with_score = onchain_graph_client.calculate_score(res)
    sorted_res = onchain_graph_client.sort_by_score(res_with_score)
    print(sorted_res[0])

asyncio.run(main())
