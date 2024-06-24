# Imports
import requests

# Trigger function that submits a secret form with a secret key
def trigger(height):
    url = "http://192.9.171.201/_REDACTED_"
    key = "_REDACTED_"
    payload={"key": key, "height": height}
    r = requests.post(url, data=payload)
    #print(r.status_code)
