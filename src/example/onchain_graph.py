import os
import asyncio
from airstack.execute_query import AirstackClient
from dotenv import load_dotenv

load_dotenv()


async def main():
    api_key = os.environ.get("AIRSTACK_API_KEY")
    if api_key is None:
        print("Please set the AIRSTACK_API_KEY environment variable")
        return

    api_client = AirstackClient(api_key=api_key)
    onchain_graph_client = api_client.onchain_graph()
    res = await onchain_graph_client.fetch_onchain_graph_data("betashop.eth")
    res_with_score = onchain_graph_client.calculate_score(res)
    sorted_res = onchain_graph_client.sort_by_score(res_with_score)
    print(sorted_res[0])

asyncio.run(main())
