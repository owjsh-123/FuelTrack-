from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Country,Region,City,FuelType,Station
class FuelTrackApiTests(TestCase):
    def setUp(self):
        ca=Country.objects.create(code='CA',name='Canada'); qc=Region.objects.create(country=ca,code='QC',name='Québec'); city=City.objects.create(region=qc,name='Montréal')
        FuelType.objects.create(code='regular',name='Regular'); self.station=Station.objects.create(name='Test',brand='Test',address='1 Test',city=city,latitude='45.5',longitude='-73.56')
        self.user=get_user_model().objects.create_user(username='u',email='u@example.com',password='strongpass123'); self.client=APIClient(); self.client.force_authenticate(self.user)
    def test_nearby(self):
        r=self.client.get('/api/stations/nearby/?lat=45.50&lon=-73.56&radius=5'); self.assertEqual(r.status_code,200); self.assertEqual(len(r.data),1)
    def test_submit_price(self):
        ft=FuelType.objects.get(code='regular'); r=self.client.post('/api/prices/',{'station':self.station.id,'fuel_type_id':ft.id,'price':'154.9'},format='json'); self.assertEqual(r.status_code,201); self.assertEqual(r.data['status'],'pending')
