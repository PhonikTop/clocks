from django.contrib import admin

from votings.models import Voting


@admin.register(Voting)
class VotingAdmin(admin.ModelAdmin):
    exclude = ("votes", "average_score", "active",)
