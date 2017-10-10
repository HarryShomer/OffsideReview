from django.conf.urls import url
from . import views

app_name = 'goalies'

urlpatterns = [
    # /goalies/
    url(r'^$', views.IndexView.as_view(), name='index'),

    url(r'^Query/', views.query_data, name='query_data'),

    url(r'^GetPlayerList/', views.get_search_list, name='search_list'),

]