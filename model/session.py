import requests


# Just A Wrapper For Debugging Session Requests
class Session(requests.Session):
    def __init__(self):
        super().__init__()

    def get(self, url, **kwargs):
        response = super().get(url, **kwargs)
        return response

    def post(self, url, data=None, json=None, **kwargs):
        response = super().post(url, data=data, json=json, **kwargs)
        return response

    def head(self, url, **kwargs):
        response = super().head(url, **kwargs)
        return response

    def close(self):
        super().close()
