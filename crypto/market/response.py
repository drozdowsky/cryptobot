import requests
import time
import logging

logger = logging.getLogger('MARKET.API')


class NotInitializedResponse(Exception):
    pass


class ServerUnavailable(Exception):
    pass


class Request:
    def __init__(self, url, retry=3):
        self._url = url
        self._retry = max(1, retry)
        self._status = -1
        self._response = None

    @property
    def status(self):
        if self._status == -1:
            raise NotInitializedResponse

        return self._status

    def get_response(self):
        retry = self._retry

        while retry > 0:
            self._response = requests.get(self._url)
            self._status = self._response.status_code

            if self._status == 200:
                break

            logger.warning('Failed {url} with {status}'.format(url=self._url, status=self._status))
            retry = retry - 1
            time.sleep(3)

    def get_json(self):
        if self._status != 200:
            self.get_response()

        if self._status == 200:
            return self._response.json()
        else:
            raise ServerUnavailable
