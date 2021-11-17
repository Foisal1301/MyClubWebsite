from django.urls import path
from . import views

urlpatterns = [
    path("",views.home,name="home"),
    path("cal/",views.cal,name="cal"),
    path('cal/<int:year>/<str:month>/',views.cal,name="cal"),
    path('events/',views.events,name="events"),
    path('events/<event_id>/',views.show_event,name="show-event"),
    path('add_venue/',views.add_venue,name="add-venue"),
    path('venues/',views.venues,name="venues"),
    path("venues/<venue_id>/",views.show_venue,name="show-venue"),
    path('search/',views.search,name='search'),
    path("update_venue/<venue_id>/",views.update_venue,name="update-venue"),
    path("add_event/",views.add_event,name="add-event"),
    path("update_event/<event_id>/",views.update_event,name="update-event"),
    path("delete_event/<event_id>/",views.delete_event,name="delete-event"),
    path("delete_venue/<venue_id>/",views.delete_venue,name="delete-venue"),
    path("venues_text/",views.venues_text,name="venues-text"),
    path('venues_csv/',views.venues_csv,name="venues-csv"),
    path('venues-pdf/',views.venues_pdf,name='venues-pdf'),
    path('my_events/',views.my_events,name='my-events')
]
