from django.urls import path
from db import views

urlpatterns = [
    path("db/", views.station_list),
    path("db/<int:pk>/", views.station_details),
    path("run_simulation/<int:sim_id>/", views.sim_request),
    path("station_suburbs", views.station_suburbs),
    path("itin_check/", views.itin_check),
]
