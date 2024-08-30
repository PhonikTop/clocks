from api.api_utils import APIResponseHandler
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

response = APIResponseHandler()


def update_participants_and_votes(room_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"room_{room_id}",
        {
            "type": "send_room_data",
        }
    )


class SocketView(APIView):
    """
    Получение информации о конкретной сессии.
    """

    def get(self, request: Request, meeting_id: int) -> Response:
        update_participants_and_votes(meeting_id)
