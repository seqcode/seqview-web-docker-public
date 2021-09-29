"""seqview URL Configuration

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
from django.contrib.auth.views import LoginView, LogoutView
from frontend import views as frontendViews
from django.urls import include, path, re_path
from rest_framework import routers
from api import views
from django.conf import settings

admin.site.index_template = 'admin/custom_index.html'
admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'seqalignments', views.getSeqalignments, basename='test')
router.register(r'assemblies', views.getAssemblies, basename='assemblies')
#router.register(r'seqalignments', views.getSeqalignmentsViewSet, basename='seqalignments')
router.register(r'higlassfiles', views.getHiGlassFilesViewSet, basename='higlassfiles')
router.register(r'annotations', views.getAnnotations, basename='annotations')
router.register(r'available-chrom-sizes',views.getAvailableChromSizes, basename='available-chrom-sizes')
router.register(r'chrom-sizes',views.ChromSizes, basename='chrom-sizes')
router.register(r'tileset_info',views.TilesetInfo, basename='tileset_info')
router.register(r'tiles',views.Tiles, basename='tiles')
router.register(r'tilesets',views.Tilesets, basename='tilesets')
router.register(r'suggest',views.Suggest, basename='suggest')
router.register(r'posttrack', views.postTrack, basename='posttrack')
router.register(r'register_url', views.RegisterURL, basename='register_url')

urlpatterns = [
	path('api/v1/tracks/<filename>', views.getTrack),
	path('api/v1/tracks/annotations/<filename>', views.getTrack),
	path('api/v1/tracks/annotations/index/<filename>', views.getTrack),	
	path('api/v1/', include(router.urls)),
	path('', include('frontend.urls')),
	path('admin/', admin.site.urls),
	path('upload/', views.adminPage),
	path('accounts/login/', LoginView.as_view(template_name='registration/login.html',), name = 'login'),
	path('accounts/logout/', LogoutView.as_view(template_name='registration/logout.html')),
	re_path(r'^(?:.*)/?$', frontendViews.index)
]

