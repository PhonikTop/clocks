from api.services.jwt_service import JWTService
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework.exceptions import AuthenticationFailed
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
from users.services.user_session_service import UserSessionService

from meetings.logic import end_meeting, meeting_results
from meetings.models import Meeting
from meetings.serializers import (
    MeetingCreateSerializer,
    MeetingInfoSerializer,
    MeetingRemoveSerializer,
    MeetingResultsSerializer,
    MeetingUpdateTaskNameSerializer,
)

MEETING_TAG = ["Meetings"]

@extend_schema(
    operation_id="createMeeting",
    summary="Создание новой встречи",
    description="Создаёт новую встречу в комнате и отправляет уведомление участникам через WebSocket",
    responses={
        201: MeetingCreateSerializer,
        400: OpenApiResponse(
            description="Некорректные данные или в комнате уже есть активная встреча",
            examples=[
                OpenApiExample(
                    "Пример ошибки",
                    value={"error": "Room meeting already exists"},
                    status_codes=[400]
                )
            ]
        )
    },
    examples=[
        OpenApiExample(
            "Пример запроса",
            value={
                "room": 1,
                "task_name": "Разработка архитектуры"
            },
            request_only=True
        ),
        OpenApiExample(
            "Пример успешного ответа",
            value={
                "id": 123,
                "room": 1,
                "task_name": "Разработка архитектуры"
            },
            response_only=True,
            status_codes=[201]
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
    operation_id="getMeeting",
    summary="Получение данных о встрече",
    description="Возвращает полные данные о встрече по её ID",
    auth=[],
    parameters=[
        OpenApiParameter(
            name="id", type=OpenApiTypes.INT, location="path", description="ID встречи"
        )
    ],
    responses={
        200: MeetingInfoSerializer,
        404: OpenApiResponse(
            description="Встреча с указанным ID не найдена",
            examples=[
                OpenApiExample(
                    "Пример ошибки", value={"detail": "Not found."}, status_codes=[404]
                )
            ],
        ),
    },
    examples=[
        OpenApiExample(
            "Пример успешного ответа",
            value={
                "id": 123,
                "room": 1,
                "task_name": "Разработка архитектуры",
                "votes": {
                    "user1_uuid": {"nickname": "User1", "vote": 5},
                    "user2_uuid": {"nickname": "User2", "vote": 8},
                },
                "average_score": 6.5,
                "active": True,
            },
            response_only=True,
        )
    ],
    tags=MEETING_TAG,
)
class GetMeetingView(RetrieveAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingInfoSerializer


@extend_schema(
    operation_id="endMeeting",
    summary="Завершение встречи",
    description="Завершает активную встречу, очищает кэш комнаты, "
                "удаляет информацию об участниках и отправляет уведомления",
    auth=[],
    methods=["PUT"],
    responses={
        200: MeetingRemoveSerializer,
        400: OpenApiResponse(description="Невозможно завершить встречу"),
        404: OpenApiResponse(
            description="Активная встреча с указанным ID не найдена",
        ),
    },
    examples=[
        OpenApiExample("Пример успешного ответа", value={"id": 123}, response_only=True)
    ],
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
    operation_id="restartMeeting",
    summary="Перезапуск встречи",
    description=(
        "Сбрасывает состояние встречи: активирует встречу, "
        "очищает голоса, сбрасывает средний балл и уведомляет участников"
    ),
    auth=[],
    methods=["PUT"],
    responses={
        200: MeetingRemoveSerializer,
        400: OpenApiResponse(description="Невозможно перезапустить встречу"),
        404: OpenApiResponse(description="Встреча с указанным ID не найдена"),
    },
    examples=[
        OpenApiExample("Пример успешного ответа", value={"id": 123}, response_only=True)
    ],
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
    operation_id="updateMeetingTask",
    summary="Обновление задачи встречи",
    description="Изменяет название текущей задачи встречи и отправляет уведомление участникам",
    auth=[],
    methods=["PUT"],
    responses={
        200: MeetingUpdateTaskNameSerializer,
        400: OpenApiResponse(
            description="Некорректное название задачи",
            examples=[
                OpenApiExample(
                    "Пример ошибки",
                    value={"task_name": ["This field is required."]},
                    status_codes=[400],
                )
            ],
        ),
        404: OpenApiResponse(
            description="Встреча с указанным ID не найдена",
            examples=[
                OpenApiExample(
                    "Пример ошибки", value={"detail": "Not found."}, status_codes=[404]
                )
            ],
        ),
    },
    examples=[
        OpenApiExample(
            "Пример запроса",
            value={"task_name": "Новое название задачи"},
            request_only=True,
        ),
        OpenApiExample(
            "Пример успешного ответа",
            value={"id": 123, "task_name": "Новое название задачи"},
            response_only=True,
        ),
    ],
    tags=MEETING_TAG,
)
class UpdateMeetingTaskView(UpdateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingUpdateTaskNameSerializer
    http_method_names = ["put"]

    def perform_update(self, serializer):
        auth_header = self.request.headers.get("Authorization")
        if not auth_header:
            raise AuthenticationFailed("Токен не предоставлен")

        if not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Неверный формат токена")

        token = auth_header.split(" ")[1]

        instance = serializer.save()
        jwt_service = JWTService()
        room_cache = RoomCacheService(instance.room)
        user_session_service = UserSessionService(jwt_service, room_cache)

        user_nickname = user_session_service.get_user_session_data(token)["nickname"]
        channel_sender = DjangoChannelMessageSender()
        room_message_service = RoomMessageService(instance.room.id, channel_sender)

        room_message_service.notify_meeting_task_name_changed(instance.task_name, user_nickname)


@extend_schema(
    operation_id="resultsMeeting",
    summary="Подведение итогов встречи",
    description=(
        "Рассчитывает и сохраняет результаты голосования, "
        "возвращает итоговые данные. Средний балл округляется до целого числа."
    ),
    auth=[],
    methods=["PUT"],
    responses={
        200: MeetingResultsSerializer,
        400: OpenApiResponse(description="Невозможно подвести итоги"),
        404: OpenApiResponse(description="Встреча с указанным ID не найдена")
    },
    examples=[
        OpenApiExample(
            "Пример успешного ответа",
            value={
                "id": 123,
                "votes": {
                    "ed445c68-f4a4-40ba-b316-9f528603481d": {
                        "nickname": "User1",
                        "vote": 4,
                    },
                    "a9115cc2-5c7c-4e1a-b5bd-61ed99c7492c": {
                        "nickname": "User2",
                        "vote": 12,
                    },
                },
                "average_score": 8.0,
            },
            response_only=True,
        )
    ],
    tags=MEETING_TAG,
)
class MeetingResultsView(UpdateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingResultsSerializer
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.get_serializer(meeting, data=request.data, partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)

        meeting_results(meeting)
        meeting.save()

        return Response(serializer.data)
