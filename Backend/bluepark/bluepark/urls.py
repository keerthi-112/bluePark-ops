"""bluepark URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('accounts/',include('accounts.urls')),
    path('',include('menu.urls')),
    path('',include('survey.urls')),
    path('payment/',include('orders.urls')),
    path('',include('kitchen.urls')),
    path('',include('inventory.urls')),
    path('',include('staff.urls')),
    path('',include('notifications.urls')),
    path('',include('core.urls')),
    path('api/v1/', include('accounts.api_urls')),
    path('api/v1/menu/', include('menu.api_urls')),
    path('api/v1/orders/', include('orders.api_urls')),
    path('api/v1/kitchen/', include('kitchen.api_urls')),
    path('api/v1/inventory/', include('inventory.api_urls')),
    path('api/v1/staff/', include('staff.api_urls')),
    path('api/v1/notifications/', include('notifications.api_urls')),
    path('admin/', admin.site.urls),
]

urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "BluePark Restaurant Services"
admin.site.index_title = 'Services'
admin.site.site_title = 'BluePark Restaurant'