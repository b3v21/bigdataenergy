from django.urls import path
from db import views

urlpatterns = [
    path("db/", views.station_list),
    path("db/<int:pk>/", views.station_details),
]
