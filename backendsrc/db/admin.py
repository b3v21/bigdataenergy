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


class PassengerChangesAdmin(admin.ModelAdmin):
    pass


class BusTimeAdmin(admin.ModelAdmin):
    pass


class BusOnRouteInfoAdmin(admin.ModelAdmin):
    pass


class StationSimAdmin(admin.ModelAdmin):
    pass


class RouteSimAdmin(admin.ModelAdmin):
    pass


class ItinerarySimAdmin(admin.ModelAdmin):
    pass


class RouteInItinCacheAdmin(admin.ModelAdmin):
    pass


class ItineraryCacheAdmin(admin.ModelAdmin):
    pass


class WalkAdmin(admin.ModelAdmin):
    pass


admin.site.register(Route, RouteAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(TravelTimes, TravelTimesAdmin)
admin.site.register(SimulationOutput, SimulationOutputAdmin)
admin.site.register(Timetable, TimetableAdmin)
admin.site.register(Shape, ShapeAdmin)
admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Trip, TripAdmin)
admin.site.register(PassengerChanges, PassengerChangesAdmin)
admin.site.register(TransporterTimeOut, BusTimeAdmin)
admin.site.register(TransporterOnRouteInfo, BusOnRouteInfoAdmin)
admin.site.register(StationSim, StationSimAdmin)
admin.site.register(RouteSim, RouteSimAdmin)
admin.site.register(ItinerarySim, ItinerarySimAdmin)
admin.site.register(RouteInItinCache, RouteInItinCacheAdmin)
admin.site.register(ItineraryCache, ItineraryCacheAdmin)
admin.site.register(Walk, WalkAdmin)
