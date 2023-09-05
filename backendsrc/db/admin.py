from django.contrib import admin
from db.models import Route, Station, TravelTimes, SimulationOutput, Timetable


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


admin.site.register(Route, RouteAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(TravelTimes, TravelTimesAdmin)
admin.site.register(SimulationOutput, SimulationOutputAdmin)
admin.site.register(Timetable, TimetableAdmin)
