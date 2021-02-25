from django.urls import path

from connection.views import RequestConnectionView, AcceptConnectionView, ListConnections

urlpatterns = [
    path('request/', RequestConnectionView.as_view(), name='connection-request'),
    path('accept/', AcceptConnectionView.as_view(), name='connection-accept'),
    path('', ListConnections.as_view(), name='connection-list')
]
