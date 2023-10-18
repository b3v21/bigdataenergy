from django.urls import path
from db import views

urlpatterns = [
    path("run_simulation/<int:sim_id>/", views.sim_request),
    path("station_suburbs", views.station_suburbs),
    path("itin_check/", views.itin_check),
    path("list_saved_sims/", views.list_saved_sims),
    path("get_sim_data/", views.get_sim_data),
]
