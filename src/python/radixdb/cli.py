import json
import aiohttp
import asyncio

async def post(url, data, headers):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json.dumps(data), headers=headers) as response:
            return await response.text()

def eval(url, text, headers={'content-type': 'application/json'}):
    return asyncio.get_event_loop().run_until_complete(post(url, {"code": text}, headers))
