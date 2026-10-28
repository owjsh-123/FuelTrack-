from rest_framework import serializers
from .models import Country,Region,City,FuelType,Station,PriceSubmission,Favorite
class CountrySerializer(serializers.ModelSerializer):
    class Meta: model=Country; fields='__all__'
class RegionSerializer(serializers.ModelSerializer):
    country=CountrySerializer(read_only=True)
    class Meta: model=Region; fields='__all__'
class CitySerializer(serializers.ModelSerializer):
    region=RegionSerializer(read_only=True)
    class Meta: model=City; fields='__all__'
class FuelTypeSerializer(serializers.ModelSerializer):
    class Meta: model=FuelType; fields='__all__'
class PriceSubmissionSerializer(serializers.ModelSerializer):
    fuel_type=FuelTypeSerializer(read_only=True)
    fuel_type_id=serializers.PrimaryKeyRelatedField(source='fuel_type',queryset=FuelType.objects.all(),write_only=True)
    submitted_by=serializers.StringRelatedField(read_only=True)
    confidence_score=serializers.ReadOnlyField()
    class Meta:
        model=PriceSubmission; fields=('id','station','fuel_type','fuel_type_id','price','submitted_by','submitted_at','status','upvotes','downvotes','source','notes','confidence_score')
        read_only_fields=('submitted_by','status','upvotes','downvotes','source')
class StationSerializer(serializers.ModelSerializer):
    city_name=serializers.CharField(source='city.name',read_only=True)
    region_code=serializers.CharField(source='city.region.code',read_only=True)
    country_code=serializers.CharField(source='city.region.country.code',read_only=True)
    latest_prices=serializers.SerializerMethodField()
    class Meta: model=Station; fields=('id','name','brand','address','postal_code','city','city_name','region_code','country_code','latitude','longitude','phone','is_active','latest_prices')
    def get_latest_prices(self,obj):
        rows=[]
        for ft in FuelType.objects.all():
            p=obj.price_submissions.filter(fuel_type=ft,status='verified').order_by('-submitted_at').first()
            if p: rows.append({'fuel_type':ft.code,'name':ft.name,'price':str(p.price),'updated_at':p.submitted_at,'confidence':p.confidence_score})
        return rows
class FavoriteSerializer(serializers.ModelSerializer):
    station_detail=StationSerializer(source='station',read_only=True)
    class Meta: model=Favorite; fields=('id','station','station_detail','created_at'); read_only_fields=('created_at',)
