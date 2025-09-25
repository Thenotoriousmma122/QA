import httpx

async def get_fact():
    url = "https://uselessfacts.jsph.pl/api/v2/facts/random"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            return f"Error with connect API"
        data = resp.json()
        return f"useless fact: \n{data['text']}"
