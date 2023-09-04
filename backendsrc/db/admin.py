from django.contrib import admin
from db.models import Route, Station, TravelTimes, SimulationOutput, Trip


class RouteAdmin(admin.ModelAdmin):
    pass


class StationAdmin(admin.ModelAdmin):
    pass


class TripAdmin(admin.ModelAdmin):
    pass

class TravelTimesAdmin(admin.ModelAdmin):
    pass


class SimulationOutputAdmin(admin.ModelAdmin):
    pass


admin.site.register(Route, RouteAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(TravelTimes, TravelTimesAdmin)
admin.site.register(SimulationOutput, SimulationOutputAdmin)
admin.site.register(Trip, TripAdmin)
