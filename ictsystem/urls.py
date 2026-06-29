from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # All app URLs are handled by the assets app
    path('', include('assets.urls')),
    
]