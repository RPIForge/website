"""forge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    #admin path
    path('admin/', admin.site.urls),

    #home page path
    path('', views.render_index, name='index'),
    path('status', views.render_status, name='status'),
    path('news', views.render_news, name='news'),
    path('hours', views.render_hours, name='hours'),
    
    #other app paths
    path('', include("myforge.urls")),
    path('', include("machine_usage.urls")),
    path('', include("data_management.urls")),
    path('', include("user_management.urls")),
    path('', include("apis.urls")),
    path('', include("business.urls"))
]

urlpatterns += staticfiles_urlpatterns()