import requests

CYBERSOURCE_URL = ""  # TODO: implement cybersource integration


def authorize_payment(payment_amount, card_data):
    # TODO: implement cybersource payment authorization
    return "NOT_IMPLEMENTED"


def cybersource_request(method, endpoint, params=None, data=None):
    # TODO: Implement cybersource authorization
    response = requests.request(
        method, f"{CYBERSOURCE_URL}/{endpoint}", params=params, data=data
    )
    if response.ok:
        return response.json()
    else:
        response.raise_for_status()
