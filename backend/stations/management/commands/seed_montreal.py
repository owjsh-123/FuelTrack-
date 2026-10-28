from django.core.management.base import BaseCommand
from stations.models import Country,Region,City,FuelType,Station
class Command(BaseCommand):
    help='Seed launch geography and example Montréal-area stations'
    def handle(self,*args,**opts):
        ca,_=Country.objects.get_or_create(code='CA',defaults={'name':'Canada','currency_code':'CAD','currency_symbol':'$','volume_unit':'litre','price_display':'cents_per_litre'})
        qc,_=Region.objects.get_or_create(country=ca,code='QC',defaults={'name':'Québec'})
        montreal,_=City.objects.get_or_create(region=qc,name='Montréal'); brossard,_=City.objects.get_or_create(region=qc,name='Brossard'); laval,_=City.objects.get_or_create(region=qc,name='Laval')
        for code,name,octane in [('regular','Regular','87'),('midgrade','Mid-Grade','89'),('premium','Premium','91+'),('diesel','Diesel','')]: FuelType.objects.get_or_create(code=code,defaults={'name':name,'octane':octane})
        examples=[('Demo Station Downtown','Demo','1000 Example St','H3A 1A1',montreal,'45.501700','-73.567300'),('Demo Station Brossard','Demo','100 Example Blvd','J4W 1A1',brossard,'45.466700','-73.450000'),('Demo Station Laval','Demo','100 Example Ave','H7N 1A1',laval,'45.606600','-73.712400')]
        for n,b,a,p,c,lat,lon in examples: Station.objects.get_or_create(name=n,city=c,defaults={'brand':b,'address':a,'postal_code':p,'latitude':lat,'longitude':lon})
        self.stdout.write(self.style.SUCCESS('Seeded Canada/Québec/Montréal launch data. Example stations are fictional.'))
