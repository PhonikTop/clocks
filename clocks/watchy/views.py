from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Room, Session, User
from .serializers import RoomSerializer, SessionSerializer, UserSerializer


@api_view(["POST"])
def join_room(request: Request) -> Response:
    """
    Присоединение пользователя к комнате.
    """
    nickname: str = request.data.get("nickname")
    room_id: int = request.data.get("room_id")
    role: str = request.data.get("role")

    # Проверка обязательных параметров
    if not nickname or not room_id or not role:
        return Response(
            {"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Проверка допустимости роли
    if role not in ["observer", "participant"]:
        return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

    # Получение комнаты
    room: Room = get_object_or_404(Room, id=room_id)

    # Обновление или создание пользователя
    user: User = User.objects.create_user(
        nickname=nickname,
        room=room,
        is_observer=role == "observer",
        state="waiting",
    )

    # Получение или создание активной сессии для комнаты
    session: Session = room.current_session
    if session is None:
        session = Session.objects.create(room=room, task_name="Default Task")
        room.current_session = session
        room.save()

    # Возврат данных пользователя и идентификатора сессии
    serializer = UserSerializer(user)
    return Response(
        {"user": serializer.data, "session_id": session.id}, status=status.HTTP_200_OK
    )


@api_view(["GET"])
def get_current_user(request: Request) -> Response:
    """
    Получение информации о текущем пользователе.
    """
    user: User = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_rooms(request: Request) -> Response:
    """
    Получение списка доступных комнат.
    """
    rooms = Room.objects.filter(is_active=True)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def create_room(request: Request) -> Response:
    """
    Создание новой комнаты.
    """
    name: str = request.data.get("name")

    if not name:
        return Response(
            {"error": "Room name is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    room: Room = Room.objects.create(name=name)
    serializer = RoomSerializer(room)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def get_room(request: Request, room_id: int) -> Response:
    """
    Получение информации о конкретной комнате.
    """
    room: Room = get_object_or_404(Room, id=room_id)
    serializer = RoomSerializer(room)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_room(request: Request, room_id: int) -> Response:
    """
    Удаление комнаты.
    """
    room: Room = get_object_or_404(Room, id=room_id)
    room.delete()
    return Response(
        {"message": "Room deleted successfully"}, status=status.HTTP_204_NO_CONTENT
    )


@api_view(["GET"])
def get_room_participants(request: Request, room_id: int) -> Response:
    """
    Получение списка участников комнаты.
    """
    room: Room = get_object_or_404(Room, id=room_id)
    data = [
        {
            "id": user.id,
            "nickname": user.nickname,
            "role": "observer" if user.is_observer else "voter",
            "state": user.state,
        }
        for user in room.users.all()
    ]
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def start_session(request: Request) -> Response:
    """
    Создание новой сессии для голосования в комнате.
    """
    room_id: int = request.data.get("room_id")
    task_name: str = request.data.get("task_name")

    if not room_id or not task_name:
        return Response(
            {"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST
        )

    room: Room = get_object_or_404(Room, id=room_id)

    # Создание новой сессии
    session: Session = Session.objects.create(room=room, task_name=task_name)
    room.current_session = session
    room.save()

    serializer = SessionSerializer(session)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def get_session(request: Request, session_id: int) -> Response:
    """
    Получение информации о конкретной сессии.
    """
    session: Session = get_object_or_404(Session, id=session_id)
    serializer = SessionSerializer(session)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def vote(request: Request, session_id: int) -> Response:
    """
    Отправка голоса участника в текущей сессии.
    """
    session: Session = get_object_or_404(Session, id=session_id)
    user_id: int = request.data.get("user_id")
    user_vote: int = request.data.get("vote")

    if not user_id or user_vote is None:
        return Response(
            {"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST
        )

    user: User = get_object_or_404(User, id=user_id)

    if user.room != session.room:
        return Response(
            {"error": "User is not in the room"}, status=status.HTTP_403_FORBIDDEN
        )

    # Установка состояния пользователя на 'voted'
    user.state = "voted"
    user.save()

    session.votes[user_id] = user_vote
    session.save()

    return Response({"message": "Vote recorded"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def end_session(request: Request, session_id: int) -> Response:
    """
    Завершение текущего раунда голосования.
    """
    session: Session = get_object_or_404(Session, id=session_id)

    if session.status == "completed":
        return Response(
            {"error": "Session already completed"}, status=status.HTTP_400_BAD_REQUEST
        )

    session.status = "completed"
    if session.votes:
        session.average_score = round(
            sum(int(value) for value in session.votes.values()) / len(session.votes)
        )
    else:
        session.average_score = 0
    session.save()

    return Response(
        {"message": "Session ended", "average_score": session.average_score},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def update_session_task(request: Request, session_id: int) -> Response:
    """
    Установка задачи для текущей сессии.
    """
    session: Session = get_object_or_404(Session, id=session_id)
    task_name: str = request.data.get("task_name")

    if not task_name:
        return Response(
            {"error": "Task name is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    session.task_name = task_name
    session.save()

    return Response(
        {"message": "Task updated", "task_name": session.task_name},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def get_room_history(request: Request, room_id: int) -> Response:
    """
    Получение истории всех сессий в комнате.
    """
    room: Room = get_object_or_404(Room, id=room_id)
    sessions = Session.objects.filter(room=room, status="completed")
    data = [
        {
            "id": session.id,
            "task_name": session.task_name,
            "average_score": session.average_score,
        }
        for session in sessions
    ]
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_session_results(request: Request, session_id: int) -> Response:
    """
    Получение результатов конкретной сессии.
    """
    session: Session = get_object_or_404(Session, id=session_id)
    results = {
        "task_name": session.task_name,
        "votes": session.votes,
        "average_score": session.average_score,
    }
    return Response(results, status=status.HTTP_200_OK)
