from functools import partial

from rest_framework import status
from rest_framework.response import Response


class APIResponseHandler:
    def __init__(self):
        # Создаем частичные функции с предустановленными параметрами
        self.success_response = partial(self.return_api_response, type_message="success")
        self.error_response = partial(self.return_api_response, type_message="error")

    def return_api_response(self, type_message: str, msg: str, data=None, response_status=status.HTTP_200_OK):
        return Response(
            {type_message: msg, "data": data}, status=response_status
        )
