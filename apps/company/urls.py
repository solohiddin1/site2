from django.urls import path
from .views import CompanyView, NewsListView, PartnersView, BannerView, ConnectWithUsView

app_name = 'company'

urlpatterns = [
    path('', CompanyView.as_view(), name='company-list'),
    path('partners/', PartnersView.as_view(), name='partners'),
    path('banners/', BannerView.as_view(), name='banners'),
    path('connect/', ConnectWithUsView.as_view(), name='connect-with-us'),
    path('connect_with_us/', ConnectWithUsView.as_view(), name='connect_with_us'),
    path('news/', NewsListView.as_view(), name='news-list'),
]
