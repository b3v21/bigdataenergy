from django.contrib import admin
from db.models import Timetable, Route, Station


class TimeTableAdmin(admin.ModelAdmin):
    pass


class RouteAdmin(admin.ModelAdmin):
    pass


class StationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Timetable, TimeTableAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(Station, StationAdmin)
