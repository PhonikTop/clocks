from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.response import Response
from rooms.services.message_senders.django_channel import DjangoChannelMessageSender
from rooms.services.room_cache_service import RoomCacheService
from rooms.services.room_message_service import RoomMessageService
from rooms.services.room_online_tracker import RoomOnlineTracker

from .logic import end_meeting, meeting_results
from .models import Meeting
from .serializers import (
    MeetingCreateSerializer,
    MeetingGetSerializer,
    MeetingRemoveSerializer,
    MeetingResultsSerializer,
    MeetingUpdateSerializer,
)

MEETING_TAG = ["Meetings"]

@extend_schema(
    summary="Создание новой встречи",
    description="Создаёт новую встречу в комнате и отправляет уведомление участникам через WebSocket",
    responses={
        201: MeetingCreateSerializer,
        400: OpenApiResponse(description="Некорректные входные данные")
    },
    examples=[
        OpenApiExample(
            "Пример запроса",
            value={
                "room": 1,
                "task_name": "Разработка архитектуры"
            },
            request_only=True
        )
    ],
    tags=MEETING_TAG,
)
class StartMeetingView(CreateAPIView):
    serializer_class = MeetingCreateSerializer

    def perform_create(self, serializer):
        instance = serializer.save(room=serializer.validated_data["room"],
                                   task_name=self.request.data.get("task_name"))

        channel_sender = DjangoChannelMessageSender()
        room_message_service = RoomMessageService(instance.room.id, channel_sender)

        room_message_service.notify_meeting_started(instance.id)


@extend_schema(
    summary="Получение данных о встрече",
    description="Возвращает полные данные о встрече по её ID",
    responses={
        200: MeetingGetSerializer,
        404: OpenApiResponse(description="Встреча не найдена")
    },
    tags=MEETING_TAG,
)
class GetMeetingView(RetrieveAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingGetSerializer


@extend_schema(
    summary="Завершение встречи",
    description="Завершает активную встречу и отправляет уведомления участникам",
    methods = ["put"],
    request=None,
    responses={
        200: MeetingRemoveSerializer,
        400: OpenApiResponse(description="Невозможно завершить встречу"),
        404: OpenApiResponse(description="Встреча не найдена")
    },
    tags=MEETING_TAG,
)
class EndMeetingView(UpdateAPIView):
    queryset = Meeting.objects.select_related("room").filter(active=True)
    serializer_class = MeetingRemoveSerializer
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.get_serializer(meeting, data=request.data, partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)

        end_meeting(meeting)
        return Response(serializer.data)


@extend_schema(
    summary="Перезапуск встречи",
    description="Сбрасывает состояние встречи, очищает голоса и уведомляет участников",
    methods = ["put"],
    request=None,
    responses={
        200: MeetingRemoveSerializer,
        400: OpenApiResponse(description="Невозможно перезапустить встречу"),
        404: OpenApiResponse(description="Встреча не найдена")
    },
    tags=MEETING_TAG,
)
class RestartMeetingView(UpdateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingRemoveSerializer
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.get_serializer(meeting, data=request.data, partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)
        channel_sender = DjangoChannelMessageSender()
        room_message_service = RoomMessageService(meeting.room.id, channel_sender)

        room_cache_service = RoomCacheService(meeting.room.id)

        meeting.reset_to_default()
        room_cache_service.clear_votes()
        RoomOnlineTracker().clean_room_offline_participants(meeting.room.id)

        room_message_service.notify_meeting_restart()

        return Response(serializer.data)


@extend_schema(
    summary="Обновление задачи встречи",
    description="Изменяет название текущей задачи встречи и отправляет уведомление",
    methods = ["put"],
    responses={
        200: MeetingUpdateSerializer,
        400: OpenApiResponse(description="Некорректное название задачи"),
        404: OpenApiResponse(description="Встреча не найдена")
    },
    tags=MEETING_TAG,
)
class UpdateMeetingTaskView(UpdateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingUpdateSerializer
    http_method_names = ["put"]

    def perform_update(self, serializer):
        instance = serializer.save()
        channel_sender = DjangoChannelMessageSender()
        room_message_service = RoomMessageService(instance.room.id, channel_sender)

        room_message_service.notify_meeting_task_name_changed(instance.task_name)


@extend_schema(
    summary="Подведение итогов встречи",
    description="Подводит итоги встречи, сохраняет их и возвращает результат",
    methods = ["put"],
    request=None,
    responses={
        200: MeetingResultsSerializer,
        400: OpenApiResponse(description="Невозможно подвести итоги"),
        404: OpenApiResponse(description="Встреча не найдена")
    },
    examples=[
        OpenApiExample(
            "Пример ответа",
            value={
                "id": 123,
                "results": {
                    "average_score": 8.5,
                    "votes": [8, 9, 8, 9, 8]
                }
            },
            response_only=True
        )
    ],
    tags=MEETING_TAG,
)
class MeetingResultsView(UpdateAPIView):
    queryset = Meeting.objects.all().filter(active=True)
    serializer_class = MeetingResultsSerializer
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.get_serializer(meeting, data=request.data, partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)

        meeting_results(meeting)
        meeting.save()

        return Response(serializer.data)
