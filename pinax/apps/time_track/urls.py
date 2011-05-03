from django.conf.urls.defaults import *



urlpatterns = patterns("",
    url(r"^$", "pinax.apps.time_track.views.overview", name="time_track_overview"),
    url(r"^upload/$", "pinax.apps.time_track.views.upload", name="time_track_upload"),
    url(r"^report/$", "pinax.apps.time_track.views.report", name="time_track_report"),
    url(r"^detail/(?P<id>\d+)/$", "pinax.apps.time_track.views.detail", name="time_track_detail"),
)
