SEARCH_HEADERS = {
    "X-Restli-Protocol-Version": "2.0.0",
    "X-Li-Pem-Metadata": "Voyager - Search Typeahead Page=global-search-typeahead-result",
    "Accept": "application/vnd.linkedin.normalized+json+2.1",
    "Csrf-Token": "ajax:3890344252407511716",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
    "Referer": "https://www.linkedin.com/feed/",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Dest": "empty",
    "Host": "www.linkedin.com",
    "Accept-Encoding": "gzip, deflate",
    "Sec-Fetch-Mode": "cors",
    "X-Li-Lang": "en_US",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Sec-Ch-Ua-Mobile": "?0",
}


INVITE = {
    'X-Restli-Protocol-Version': '2.0.0',
    'X-Li-Deco-Include-Micro-Schema': 'true',
    'X-Li-Pem-Metadata': 'Voyager - Invitations=send-invite',
}

INVITE_PARAM = {
    'action': 'verifyQuotaAndCreate',
    'decorationId': 'com.linkedin.voyager.dash.deco.relationships.InvitationCreationResultWithInvitee-2',
}

INVITE_DATA = {
    'customMessage': '',
    'inviteeProfileUrn': 'urn:li:fsd_profile:ACoAABfBQIcBIX_A-IoC-vywpD4X0NGe9MPy2xE',
}

MSG_PAYLOAD = {
    "message": {
        "body": {
            "text": "testing something",
            "attributes": []
        },
        "originToken": "2c7a017d-7a38-475f-a8a8-28d16ae5a80d",
        "renderContentUnions": []
    },
    "mailboxUrn": "urn:li:fsd_profile:ACoAACxCL6cBdoFZwjMOKgZbAP8-oZkEONxtp14",
    "trackingId": "",
    "dedupeByClientGeneratedToken": False,
    "hostRecipientUrns": [
        "urn:li:fsd_profile:ACoAADZYKf8BjazA7rIr3-hIhnVjRduHCUXmQg0"
    ]
}

DELAY = 15
SLEEP_RANGE = [i / 10 for i in range(10, DELAY * 10)]
MESSAGE = "Hi"
