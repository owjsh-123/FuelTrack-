from django.conf import settings
from django.db import models
from django.utils import timezone

class Country(models.Model):
    code=models.CharField(max_length=2,unique=True)
    name=models.CharField(max_length=80)
    currency_code=models.CharField(max_length=3,default='CAD')
    currency_symbol=models.CharField(max_length=8,default='$')
    volume_unit=models.CharField(max_length=16,default='litre')
    price_display=models.CharField(max_length=30,default='cents_per_litre')
    def __str__(self): return self.name

class Region(models.Model):
    country=models.ForeignKey(Country,on_delete=models.CASCADE,related_name='regions')
    code=models.CharField(max_length=10)
    name=models.CharField(max_length=80)
    class Meta: unique_together=('country','code')
    def __str__(self): return f'{self.name}, {self.country.code}'

class City(models.Model):
    region=models.ForeignKey(Region,on_delete=models.CASCADE,related_name='cities')
    name=models.CharField(max_length=100)
    def __str__(self): return f'{self.name}, {self.region.code}'

class FuelType(models.Model):
    code=models.SlugField(max_length=40,unique=True)
    name=models.CharField(max_length=60)
    octane=models.CharField(max_length=20,blank=True)
    def __str__(self): return self.name

class Station(models.Model):
    name=models.CharField(max_length=120)
    brand=models.CharField(max_length=80,blank=True)
    address=models.CharField(max_length=200)
    postal_code=models.CharField(max_length=20,blank=True)
    city=models.ForeignKey(City,on_delete=models.PROTECT,related_name='stations')
    latitude=models.DecimalField(max_digits=9,decimal_places=6)
    longitude=models.DecimalField(max_digits=9,decimal_places=6)
    phone=models.CharField(max_length=30,blank=True)
    is_active=models.BooleanField(default=True)
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='stations_created')
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.name} — {self.city.name}'

class PriceSubmission(models.Model):
    STATUS=(('pending','Pending'),('verified','Verified'),('rejected','Rejected'))
    station=models.ForeignKey(Station,on_delete=models.CASCADE,related_name='price_submissions')
    fuel_type=models.ForeignKey(FuelType,on_delete=models.PROTECT,related_name='submissions')
    price=models.DecimalField(max_digits=8,decimal_places=3,help_text='Local displayed price, e.g. 154.9 cents/L in Canada')
    submitted_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,related_name='price_submissions')
    submitted_at=models.DateTimeField(default=timezone.now)
    status=models.CharField(max_length=12,choices=STATUS,default='pending')
    upvotes=models.PositiveIntegerField(default=0)
    downvotes=models.PositiveIntegerField(default=0)
    source=models.CharField(max_length=30,default='community')
    notes=models.CharField(max_length=240,blank=True)
    class Meta: ordering=['-submitted_at']
    @property
    def confidence_score(self):
        total=self.upvotes+self.downvotes
        return round(self.upvotes/total,3) if total else 0.5

class PriceVote(models.Model):
    VOTE=((1,'Accurate'),(-1,'Inaccurate'))
    submission=models.ForeignKey(PriceSubmission,on_delete=models.CASCADE,related_name='votes')
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    value=models.SmallIntegerField(choices=VOTE)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: unique_together=('submission','user')

class Favorite(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='favorites')
    station=models.ForeignKey(Station,on_delete=models.CASCADE,related_name='favorited_by')
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: unique_together=('user','station')
