from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

#from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include(('user.urls', 'user'), namespace='user')),
    path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('connection/', include(('connection.urls',
                                 'connection'), namespace='connection')),
    path('chat/', include(('chat.urls', 'chat'), namespace='chat')),
    path('task/', include(('task.urls', 'task'), namespace='task'))
]
