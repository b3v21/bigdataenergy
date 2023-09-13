from django.contrib import admin
from db.models import *


class RouteAdmin(admin.ModelAdmin):
    pass


class StationAdmin(admin.ModelAdmin):
    pass


class TimetableAdmin(admin.ModelAdmin):
    pass


class TravelTimesAdmin(admin.ModelAdmin):
    pass


class SimulationOutputAdmin(admin.ModelAdmin):
    pass


class ShapeAdmin(admin.ModelAdmin):
    pass


class CalendarAdmin(admin.ModelAdmin):
    pass


class TripAdmin(admin.ModelAdmin):
    pass


admin.site.register(Route, RouteAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(TravelTimes, TravelTimesAdmin)
admin.site.register(SimulationOutput, SimulationOutputAdmin)
admin.site.register(Timetable, TimetableAdmin)
admin.site.register(Shape, ShapeAdmin)
admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Trip, TripAdmin)
