from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',  TemplateView.as_view(template_name="home.html"), name='home'),
    url(r'^goalies/', include('goalies.urls')),
    url(r'^skaters/', include('skaters.urls')),
    url(r'^teams/', include('teams.urls')),
    url(r'^gamepredictions/', include('game_preds.urls')),
    url(r'^seasonprojections/', include('season_projs.urls')),
    url(r'^glossary/', TemplateView.as_view(template_name="glossary.html"), name='glossary'),
    url(r'^about/', TemplateView.as_view(template_name="about.html"), name='about')
]
