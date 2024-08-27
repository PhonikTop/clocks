from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rooms.models import Room

from .models import Session
from .serializers import SessionSerializer


class StartSessionView(APIView):
    """
    Создание новой сессии для голосования в комнате.
    """

    def post(self, request: Request) -> Response:
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


class GetSessionView(APIView):
    """
    Получение информации о конкретной сессии.
    """

    def get(self, request: Request, session_id: int) -> Response:
        session = get_object_or_404(Session, id=session_id)
        serializer = SessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VoteView(APIView):
    """
    Отправка голоса участника в текущей сессии.
    """

    def post(self, request: Request, session_id: int) -> Response:
        session = get_object_or_404(Session, id=session_id)
        user_name = request.data.get("user")
        user_vote = request.data.get("vote")

        if not user_name or user_vote is None:
            return Response(
                {"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST
            )

        session.votes[user_name] = user_vote
        session.save()

        return Response({"message": "Vote recorded"}, status=status.HTTP_200_OK)


class EndSessionView(APIView):
    """
    Завершение текущего раунда голосования.
    """

    def post(self, request: Request, session_id: int) -> Response:
        session = get_object_or_404(Session, id=session_id)

        if not session.active:
            return Response(
                {"error": "Session already completed"}, status=status.HTTP_400_BAD_REQUEST
            )

        session.active = False
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


class UpdateSessionTaskView(APIView):
    """
    Установка задачи для текущей сессии.
    """

    def post(self, request: Request, session_id: int) -> Response:
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


class GetSessionResultsView(APIView):
    """
    Получение результатов конкретной сессии.
    """

    def get(self, request: Request, session_id: int) -> Response:
        session = get_object_or_404(Session, id=session_id)
        results = {
            "task_name": session.task_name,
            "votes": session.votes,
            "average_score": session.average_score,
        }
        return Response(results, status=status.HTTP_200_OK)
