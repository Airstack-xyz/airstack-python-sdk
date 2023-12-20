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
    res = await onchain_graph_client.fetch_onchain_graph_data("yosephks.eth")
    print(len(res), res if len(res) > 0 else "No data found")

asyncio.run(main())
