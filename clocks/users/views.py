from django.http import Http404
from django.shortcuts import get_object_or_404
from meetings.models import Meeting
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rooms.models import Room

from .redis_client import RedisClient
from .serializers import UserInputSerializer

redis = RedisClient()


class JoinRoomView(CreateAPIView):
    """
    Присоединение пользователя к комнате.
    """
    serializer_class = UserInputSerializer

    def perform_create(self, serializer):
        nickname, role = serializer.validated_data["nickname"], serializer.validated_data["role"]
        cookie = self.request.COOKIES.get("user")

        if redis.check_token_in_db(cookie):
            raise ValidationError({"error": "User exists"})

        redis.save_new_client_to_redis(cookie, nickname, role)

        room = get_object_or_404(Room, id=self.request.data.get("room_id"))
        room.participants.append({cookie: role})

        meeting = room.current_meeting or Meeting.objects.create(room=room, task_name="Введите название таска")
        meeting.votes[cookie] = None

        room.current_meeting = meeting
        room.save()


class CurrentUserView(RetrieveAPIView):
    """
    Получение информации о текущем пользователе.
    """
    serializer_class = UserInputSerializer

    def get_object(self):
        cookie = self.request.COOKIES.get("user")
        if cookie is None:
            raise Http404("User cookie not found")
        user_data = redis.get_client_data_by_cookie(cookie)
        if not all(user_data.values()):
            raise Http404("User not found")
        return user_data
