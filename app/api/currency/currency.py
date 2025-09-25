import httpx

API_KEY = 'cur_live_xe5ZFwwptPbjyQeCjyLHfTDv6n2SNRZiqKj3rVRk'

async def get_currency_rates() -> str:
    url = f"https://api.currencyapi.com/v3/latest?apikey={API_KEY}&base_currency=KZT&currencies=USD,EUR,RUB,BTC"

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                return f"Error with connect API: {resp.status_code}"

            data = resp.json()["data"]

            kzt_to_usd = data["USD"]["value"]
            kzt_to_eur = data["EUR"]["value"]
            kzt_to_rub = data["RUB"]["value"]
            kzt_to_btc = data["BTC"]["value"]


            usd_to_kzt = 1 / kzt_to_usd
            eur_to_kzt = 1 / kzt_to_eur
            rub_to_kzt = 1 / kzt_to_rub
            btc_to_kzt = 1 / kzt_to_btc

            return (
                f"💱 Actual Course:\n\n"
                f"🇺🇸 1 USD = {usd_to_kzt:,.2f} ₸\n"
                f"🇪🇺 1 EUR = {eur_to_kzt:,.2f} ₸\n"
                f"🇷🇺 1 RUB = {rub_to_kzt:,.2f} ₸\n"
                f"₿ 1 Bitcoin = {btc_to_kzt:,.2f} ₸"
            )
        except Exception as e:
            return f"Error with getting data: {str(e)}"