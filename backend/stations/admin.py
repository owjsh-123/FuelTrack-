from django.contrib import admin
from .models import Country,Region,City,FuelType,Station,PriceSubmission,PriceVote,Favorite
@admin.register(Station)
class StationAdmin(admin.ModelAdmin): list_display=('name','brand','city','postal_code','is_active'); search_fields=('name','brand','address','postal_code'); list_filter=('is_active','city__region__country')
@admin.register(PriceSubmission)
class PriceAdmin(admin.ModelAdmin): list_display=('station','fuel_type','price','status','submitted_by','submitted_at','upvotes','downvotes'); list_filter=('status','fuel_type','station__city__region__country'); actions=['verify']
@admin.action(description='Mark selected prices verified')
def verify(self,request,queryset): queryset.update(status='verified')
admin.site.register([Country,Region,City,FuelType,PriceVote,Favorite])
