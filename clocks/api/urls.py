from django.urls import include, path

# Import views from all api applications
from meetings import views as meetings
# from rooms import views as rooms
from users import views as users

urlpatterns = [
    path("user/join-room", users.join_room, name="join_room"),
    path("user/current", users.get_current_user, name="get_current_user"),

    # path("rooms", rooms.get_rooms, name="get_rooms"),
    # path("room", rooms.create_room, name="create_room"),
    # path("room/get/<int:room_id>", rooms.get_room, name="get_room"),
    # path("room/del/<int:room_id>", rooms.delete_room, name="delete_room"),
    # path("room/<int:room_id>/participants", rooms.get_room_participants, name="get_room_participants"),
    # path("room/<int:room_id>/history", rooms.get_room_history, name="get_room_history"),
    path("room/", include("rooms.urls")),

    path("session", meetings.start_session, name="start_session"),
    path("session/<int:session_id>", meetings.get_session, name="get_session"),
    path("session/<int:session_id>/vote", meetings.vote, name="vote"),
    path("session/<int:session_id>/end", meetings.end_session, name="end_session"),
    path("session/<int:session_id>/task", meetings.update_session_task, name="update_session_task"),
    path("session/<int:session_id>/results", meetings.get_session_results, name="get_session_results"),
]
