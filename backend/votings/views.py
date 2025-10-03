import structlog
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

from votings.logic import end_voting, voting_results
from votings.models import Voting
from votings.serializers import (
    VotingCreateSerializer,
    VotingInfoSerializer,
    VotingRemoveSerializer,
    VotingResultsSerializer,
    VotingUpdateTaskNameSerializer,
)

logger = structlog.get_logger()

VOTING_TAG = ["Votings"]

@extend_schema(
    operation_id="createVoting",
    summary="Создание нового голосование",
    description="Создаёт новое голосование в комнате и отправляет уведомление участникам через WebSocket",
    responses={
        201: VotingCreateSerializer,
        400: OpenApiResponse(
            description="Некорректные данные или в комнате уже есть активное голосование",
            examples=[
                OpenApiExample(
                    "Пример ошибки",
                    value={"error": "Room voting already exists"},
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
    tags=VOTING_TAG,
)
class StartVotingView(CreateAPIView):
    serializer_class = VotingCreateSerializer

    def perform_create(self, serializer):
        instance = serializer.save(room=serializer.validated_data["room"],
                                   task_name=self.request.data.get("task_name"))

        channel_sender = DjangoChannelMessageSender()
        room_message_service = RoomMessageService(instance.room.id, channel_sender)

        logger.info("Голосование запущено", room=instance.room.id)
        room_message_service.notify_voting_started(instance.id)


@extend_schema(
    operation_id="getVoting",
    summary="Получение данных о голосовании",
    description="Возвращает полные данные о голосовании по его ID",
    auth=[],
    parameters=[
        OpenApiParameter(
            name="id", type=OpenApiTypes.INT, location="path", description="ID голосования"
        )
    ],
    responses={
        200: VotingInfoSerializer,
        404: OpenApiResponse(
            description="Голосование с указанным ID не найдено",
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
    tags=VOTING_TAG,
)
class GetVotingView(RetrieveAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingInfoSerializer


@extend_schema(
    operation_id="endVoting",
    summary="Завершение голосования",
    description="Завершает активное голосование, очищает кэш комнаты, "
                "удаляет информацию об участниках и отправляет уведомления",
    auth=[],
    methods=["PUT"],
    responses={
        200: VotingRemoveSerializer,
        400: OpenApiResponse(description="Невозможно завершить голосование"),
        404: OpenApiResponse(
            description="Активное голосование с указанным ID не найдено",
        ),
    },
    examples=[
        OpenApiExample("Пример успешного ответа", value={"id": 123}, response_only=True)
    ],
    tags=VOTING_TAG,
)
class EndVotingView(UpdateAPIView):
    queryset = Voting.objects.select_related("room").filter(active=True)
    serializer_class = VotingRemoveSerializer
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        voting = self.get_object()
        serializer = self.get_serializer(voting, data=request.data, partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)

        end_voting(voting)
        logger.info("Голосование завершено", room=voting.room.id, voting=voting.id)
        return Response(serializer.data)


@extend_schema(
    operation_id="restartVoting",
    summary="Перезапуск голосования",
    description=(
        "Сбрасывает состояние голосования: активирует голосование, "
        "очищает голоса, сбрасывает средний балл и уведомляет участников"
    ),
    auth=[],
    methods=["PUT"],
    responses={
        200: VotingRemoveSerializer,
        400: OpenApiResponse(description="Невозможно перезапустить голосование"),
        404: OpenApiResponse(description="Голосование с указанным ID не найдено"),
    },
    examples=[
        OpenApiExample("Пример успешного ответа", value={"id": 123}, response_only=True)
    ],
    tags=VOTING_TAG,
)
class RestartVotingView(UpdateAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingRemoveSerializer
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        voting = self.get_object()
        serializer = self.get_serializer(voting, data=request.data, partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)
        channel_sender = DjangoChannelMessageSender()
        room_message_service = RoomMessageService(voting.room.id, channel_sender)

        room_cache_service = RoomCacheService(voting.room.id)

        voting.reset_to_default()
        room_cache_service.clear_votes()
        RoomOnlineTracker().clean_room_offline_participants(voting.room.id)

        logger.info("Голосование перезапущено", room=voting.room.id, voting=voting.id)
        room_message_service.notify_voting_restart()

        return Response(serializer.data)


@extend_schema(
    operation_id="updateVotingTask",
    summary="Обновление задачи голосования",
    description="Изменяет название текущей задачи голосования и отправляет уведомление участникам",
    auth=[],
    methods=["PUT"],
    responses={
        200: VotingUpdateTaskNameSerializer,
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
            description="Голосование с указанным ID не найдено",
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
    tags=VOTING_TAG,
)
class UpdateVotingTaskView(UpdateAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingUpdateTaskNameSerializer
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

        user_data = user_session_service.get_user_session_data(token)

        logger.info(
            "Описание задачи голосования изменено",
            room=instance.room,
            user=user_data["user_uuid"],
            new_task_name=instance.task_name,
        )

        channel_sender = DjangoChannelMessageSender()
        room_message_service = RoomMessageService(instance.room.id, channel_sender)

        room_message_service.notify_voting_task_name_changed(instance.task_name, user_data["nickname"])


@extend_schema(
    operation_id="resultsVoting",
    summary="Подведение итогов голосования",
    description=(
        "Рассчитывает и сохраняет результаты голосования, "
        "возвращает итоговые данные. Средний балл округляется до целого числа."
    ),
    auth=[],
    methods=["PUT"],
    responses={
        200: VotingResultsSerializer,
        400: OpenApiResponse(description="Невозможно подвести итоги"),
        404: OpenApiResponse(description="Голосование с указанным ID не найдено")
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
    tags=VOTING_TAG,
)
class VotingResultsView(UpdateAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingResultsSerializer
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        voting = self.get_object()
        serializer = self.get_serializer(voting, data=request.data, partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)

        voting_results(voting)
        voting.save()

        return Response(serializer.data)
