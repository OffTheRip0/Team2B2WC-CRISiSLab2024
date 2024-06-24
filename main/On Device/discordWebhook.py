import requests

url = "_REDACTED_"

def send(height):
    data = {
        "content" : "",
        "username" : "2B2WC Alerts Webhook"
    }

    desc = (f"Get To Higher Ground, a wave with the height of {height}cm will hit shore soon with more to come.")
    data["embeds"] = [
        {
            "description" : desc,
            "title" : "Tsunami Alert!"
        }
    ]

    result = requests.post(url, json = data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)