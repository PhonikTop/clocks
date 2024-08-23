from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Room, User, Session
from .serializers import UserSerializer, RoomSerializer, SessionSerializer


@api_view(["POST"])
def join_room(request):
    """
    Присоединение пользователя к комнате.
    """
    nickname = request.data.get("nickname")
    room_id = request.data.get("room_id")
    role = request.data.get("role")

    # Проверка обязательных параметров
    if not nickname or not room_id or not role:
        return Response(
            {"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Проверка допустимости роли
    if role not in ["observer", "participant"]:
        return Response(
            {"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Получение комнаты
    room = get_object_or_404(Room, id=room_id)
    # Обновление или создание пользователя
    print(nickname)
    user = User.objects.create_user(
        nickname=nickname,
        username=nickname,
        room=room,
        is_observer=role == "observer",
        state="waiting"
    )

    # Получение или создание активной сессии для комнаты
    session = room.current_session
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
def get_current_user(request):
    """
    Получение информации о текущем пользователе.
    """
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_rooms(request):
    """
    Получение списка доступных комнат.
    """
    rooms = Room.objects.filter(is_active=True)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def create_room(request):
    """
    Создание новой комнаты.
    """
    name = request.data.get("name")
    print(name)
    if not name:
        return Response(
            {"error": "Room name is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    room = Room.objects.create(name=name)
    serializer = RoomSerializer(room)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def get_room(request, room_id):
    """
    Получение информации о конкретной комнате.
    """
    room = get_object_or_404(Room, id=room_id)
    serializer = RoomSerializer(room)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_room(request, room_id):
    """
    Удаление комнаты.
    """
    room = get_object_or_404(Room, id=room_id)
    room.delete()
    return Response(
        {"message": "Room deleted successfully"}, status=status.HTTP_204_NO_CONTENT
    )


@api_view(["GET"])
def get_room_participants(request, room_id):
    """
    Получение списка участников комнаты.
    """
    room = get_object_or_404(Room, id=room_id)
    participants = room.users.all()
    data = [
        {
            "id": user.id,
            "nickname": user.nickname,
            "role": "observer" if user.is_observer else "voter",
            "state": user.state,
        }
        for user in participants
    ]
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def start_session(request):
    """
    Создание новой сессии для голосования в комнате.
    """
    room_id = request.data.get("room_id")
    task_name = request.data.get("task_name")

    if not room_id or not task_name:
        return Response(
            {"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST
        )

    room = get_object_or_404(Room, id=room_id)

    # Создание новой сессии
    session = Session.objects.create(room=room, task_name=task_name)
    room.current_session = session
    room.save()

    serializer = SessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def get_session(request, session_id):
    """
    Получение информации о конкретной сессии.
    """
    session = get_object_or_404(Session, id=session_id)
    serializer = SessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def vote(request, session_id):
    """
    Отправка голоса участника в текущей сессии.
    """
    session = get_object_or_404(Session, id=session_id)
    user_id = request.data.get("user_id")
    user_vote = request.data.get("vote")

    if not user_id or user_vote is None:
        return Response(
            {"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST
        )

    user = get_object_or_404(User, id=user_id)

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
def end_session(request, session_id):
    """
    Завершение текущего раунда голосования.
    """
    session = get_object_or_404(Session, id=session_id)

    if session.status == "completed":
        return Response(
            {"error": "Session already completed"}, status=status.HTTP_400_BAD_REQUEST
        )

    session.status = "completed"
    session.average_score = 0 if not votes else round(sum(session.votes.values()) / len(session.votes))

    session.save()

    return Response(
        {"message": "Session ended", "average_score": session.average_score},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def update_session_task(request, session_id):
    """
    Установка задачи для текущей сессии.
    """
    session = get_object_or_404(Session, id=session_id)
    task_name = request.data.get("task_name")

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
def get_room_history(request, room_id):
    """
    Получение истории всех сессий в комнате.
    """
    room = get_object_or_404(Room, id=room_id)
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
def get_session_results(request, session_id):
    """
    Получение результатов конкретной сессии.
    """
    session = get_object_or_404(Session, id=session_id)
    results = {
        "task_name": session.task_name,
        "votes": session.votes,
        "average_score": session.average_score,
    }
    return Response(results, status=status.HTTP_200_OK)
