from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('www.urls')),
    path('api/', include('www.api_urls')),
    path('api/auth/token/', TokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('api/auth/token/refresh/',TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('djoser.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
