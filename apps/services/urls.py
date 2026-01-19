from django.urls import path
from .views import CityListView, ServiceLocationListView, ServiceCenterDescriptionListView, StoreListView

app_name = 'services'

urlpatterns = [
    # path('cities/', CityListView.as_view(), name='city-list'),
    # path('locations/', ServiceLocationListView.as_view(), name='service-locations'),
    # path('descriptions/', ServiceCenterDescriptionListView.as_view(), name='service-descriptions'),
    path('stores/', StoreListView.as_view(), name='store-list'),
]
