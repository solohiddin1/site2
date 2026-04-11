from django.urls import path
from .views import CityListView, ServiceLocationListView, ServiceCenterDescriptionListView, StoreListView, ContactsListView

app_name = 'services'

urlpatterns = [
    path('stores/', StoreListView.as_view(), name='store-list'),
    path('contacts/', ContactsListView.as_view(), name='contacts-list'),
]
