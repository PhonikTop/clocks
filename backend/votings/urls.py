from django.urls import path

from votings.views import (
    EndVotingView,
    GetVotingView,
    RestartVotingView,
    StartVotingView,
    UpdateVotingTaskView,
    VotingResultsView,
)

urlpatterns = [
    path("", StartVotingView.as_view(), name="start_voting"),
    path("<int:pk>", GetVotingView.as_view(), name="get_voting"),
    path("<int:pk>/end", EndVotingView.as_view(), name="end_voting"),
    path("<int:pk>/restart", RestartVotingView.as_view(), name="restart_voting"),
    path("<int:pk>/task", UpdateVotingTaskView.as_view(), name="update_voting_task"),
    path("<int:pk>/results", VotingResultsView.as_view(), name="get_voting_results"),
]
