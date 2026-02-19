from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField
from .models import City, ServiceLocation, ServiceCenterDescription, Store, Contacts


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']


class ServiceCenterDescriptionSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=ServiceCenterDescription)

    class Meta:
        model = ServiceCenterDescription
        fields = ['id', 'translations']


class ServiceLocationSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    description = ServiceCenterDescriptionSerializer(read_only=True)

    class Meta:
        model = ServiceLocation
        fields = ['id', 'city', 'address', 'phone', 'email', 'map_url', 'description']


class StoreSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Store)

    class Meta:
        model = Store
        fields = ['id', 'translations', 'address', 'phone', 'email', 'map_url', 'lat', 'long']


class ContactsSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Contacts)

    class Meta:
        model = Contacts
        fields = [
            'id',
            'translations',
            'phone_number',
            'email',
            'lat',
            'long',
            'start_day',
            'end_day',
            'start_time',
            'end_time',
        ]
