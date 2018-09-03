from django.conf.urls import url
from . import views

app_name = 'game_preds'

urlpatterns = [
    # /gamepredictions/
    url(r'^$', views.IndexView.as_view(), name='index'),

    url(r'^Query/', views.query_data, name='query_data'),
]