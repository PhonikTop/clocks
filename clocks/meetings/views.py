from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rooms.models import Room

from .models import Meeting
from .serializers import MeetingSerializer


class StartMeetingView(APIView):
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

        meeting = Meeting.objects.create(room=room, task_name=task_name)
        room.current_meeting = meeting
        room.save()

        serializer = MeetingSerializer(meeting)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetMeetingView(APIView):
    """
    Получение информации о конкретной сессии.
    """

    def get(self, request: Request, meeting_id: int) -> Response:
        meeting = get_object_or_404(Meeting, id=meeting_id)
        serializer = MeetingSerializer(meeting)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VoteView(APIView):
    """
    Отправка голоса участника в текущей сессии.
    """

    def post(self, request: Request, meeting_id: int) -> Response:
        meeting = get_object_or_404(Meeting, id=meeting_id)
        user_name = request.data.get("user")
        user_vote = request.data.get("vote")

        if not user_name or user_vote is None:
            return Response(
                {"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST
            )
        room: Room = get_object_or_404(Room, current_meeting_id=meeting_id)
        if not any(user_name in d for d in room.users):
            return Response(
                {"error": "Participant doesn't exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        meeting.votes[user_name] = user_vote
        meeting.save()

        return Response({"message": "Vote recorded"}, status=status.HTTP_200_OK)


class EndMeetingView(APIView):
    """
    Завершение текущего раунда голосования.
    """

    def post(self, request: Request, meeting_id: int) -> Response:
        meeting = get_object_or_404(Meeting, id=meeting_id)

        if not meeting.active:
            return Response(
                {"error": "Meeting already completed"}, status=status.HTTP_400_BAD_REQUEST
            )

        meeting.active = False
        if meeting.votes:
            meeting.average_score = round(
                sum(int(value) for value in meeting.votes.values()) / len(meeting.votes)
            )
        else:
            meeting.average_score = 0
        meeting.save()

        return Response(
            {"message": "Meeting ended", "average_score": meeting.average_score},
            status=status.HTTP_200_OK,
        )


class UpdateMeetingTaskView(APIView):
    """
    Установка задачи для текущей сессии.
    """

    def post(self, request: Request, meeting_id: int) -> Response:
        meeting = get_object_or_404(Meeting, id=meeting_id)
        task_name = request.data.get("task_name", )

        if not task_name:
            return Response(
                {"error": "Task name is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        meeting.task_name = task_name
        meeting.save()

        return Response(
            {"message": "Task updated", "task_name": meeting.task_name},
            status=status.HTTP_200_OK,
        )


class GetMeetingResultsView(APIView):
    """
    Получение результатов конкретной сессии.
    """

    def get(self, request: Request, meeting_id: int) -> Response:
        meeting = get_object_or_404(Meeting, id=meeting_id)
        results = {
            "task_name": meeting.task_name,
            "votes": meeting.votes,
            "average_score": meeting.average_score,
        }
        return Response(results, status=status.HTTP_200_OK)
