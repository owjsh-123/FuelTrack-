from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CountryViewSet,RegionViewSet,CityViewSet,FuelTypeViewSet,StationViewSet,PriceSubmissionViewSet,FavoriteViewSet,analytics
r=DefaultRouter(); r.register('countries',CountryViewSet); r.register('regions',RegionViewSet); r.register('cities',CityViewSet); r.register('fuel-types',FuelTypeViewSet); r.register('stations',StationViewSet); r.register('prices',PriceSubmissionViewSet); r.register('favorites',FavoriteViewSet,basename='favorite')
urlpatterns=[path('',include(r.urls)),path('analytics/',analytics)]
