from rest_framework.views import APIView
from rest_framework.response import Response
from .models import City, ServiceLocation, ServiceCenterDescription, Store
from .serializers import CitySerializer, ServiceLocationSerializer, ServiceCenterDescriptionSerializer, StoreSerializer


class CityListView(APIView):
    """List all cities"""
    def get(self, request):
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True, context={'request': request})
        return Response(serializer.data)


class ServiceLocationListView(APIView):
    """List all service locations"""
    def get(self, request):
        service_locations = ServiceLocation.objects.all()
        serializer = ServiceLocationSerializer(service_locations, many=True, context={'request': request})
        return Response(serializer.data)


class ServiceCenterDescriptionListView(APIView):
    """List service center descriptions"""
    def get(self, request):
        service_center_descriptions = ServiceCenterDescription.objects.all()
        serializer = ServiceCenterDescriptionSerializer(service_center_descriptions, many=True, context={'request': request})
        return Response(serializer.data)


class StoreListView(APIView):
    """List all stores"""
    def get(self, request):
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True, context={'request': request})
        return Response(serializer.data)
