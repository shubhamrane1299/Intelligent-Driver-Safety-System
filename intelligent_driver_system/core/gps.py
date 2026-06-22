
import requests

def get_location():

    try:

        response = requests.get(

            "https://ipinfo.io/json",

            timeout=5

        )

        data = response.json()

        return {

            "city": data.get("city", "Unknown"),

            "region": data.get("region", "Unknown"),

            "country": data.get("country", "Unknown")

        }

    except Exception as e:

        print("GPS ERROR :", e)

        return {

            "city": "Unknown",

            "region": "Unknown",

            "country": "Unknown"

        }

