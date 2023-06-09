__author__ = 'sarvesh.singh'

import json
import aiohttp
from airstack.constant import AirstackConstants


class SendRequest:
    """
    Send Request
    """

    @staticmethod
    async def send_post_request(url=None, headers=None, data=None,
                                timeout=True):
        """Async function to send post request

        Args:
            url (str, optional): server url. Defaults to None.
            headers (dict, optional): headers. Defaults to None.
            data (dict, optional): json request body. Defaults to None.
            timeout (int, optional): timeout for api. Defaults to True.

        Returns:
            Tuple: JSON response or None, response status code, error message or None
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url=url, headers=headers,
                                        data=data,
                                        timeout=timeout) as response:
                    content = await response.text()
                    try:
                        nt = json.loads(content)
                    except json.JSONDecodeError:
                        nt = json.loads(json.dumps(content))

                    if response.status != AirstackConstants.SUCCESS_STATUS_CODE:
                        if response.status == AirstackConstants.UNPROCESSABLE_STATUS_CODE:
                            return None, response.status, response.reason
                        return None, response.status, nt["error"]

                    if "errors" in nt:
                        return nt, response.status, nt["errors"]

                    return nt["data"], response.status, None
            except Exception as exec:
                return None, response.status, str(exec)
