from django.urls import include, path
import nmk.settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    path('', include('nmkapp.urls')),
    path('admin/', admin.site.urls),
]

if nmk.settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(
        path('__debug__/', include(debug_toolbar.urls))
    )