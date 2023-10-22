from django.urls import path, include
from .views import DataView, GlobalView, TournamentView, TeamView, TeamAllView, GlobalAllView
from django.views.decorators.csrf import csrf_exempt

app_name = 'data'

urlpatterns = [
    path(r'data/', csrf_exempt(DataView.as_view()), name='Data'),
    path(r'global/', csrf_exempt(GlobalView.as_view()), name='Global'),
    path(r'tournament/', csrf_exempt(TournamentView.as_view()), name='Tournament'),
    path(r'team/', csrf_exempt(TeamView.as_view()), name='Team'),
    path(r'teamall/', csrf_exempt(TeamAllView.as_view()), name='TeamAll'),
    path(r'globalall/', csrf_exempt(GlobalAllView.as_view()), name='GlobalAll')
]