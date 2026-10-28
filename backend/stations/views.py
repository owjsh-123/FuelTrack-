from math import radians, sin, cos, asin, sqrt
from django.db.models import Avg
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .models import Country,Region,City,FuelType,Station,PriceSubmission,PriceVote,Favorite
from .serializers import CountrySerializer,RegionSerializer,CitySerializer,FuelTypeSerializer,StationSerializer,PriceSubmissionSerializer,FavoriteSerializer

def distance_km(lat1,lon1,lat2,lon2):
    lon1,lat1,lon2,lat2=map(radians,map(float,[lon1,lat1,lon2,lat2])); dlon=lon2-lon1; dlat=lat2-lat1
    a=sin(dlat/2)**2+cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 6371*2*asin(sqrt(a))

class CountryViewSet(viewsets.ReadOnlyModelViewSet): queryset=Country.objects.all(); serializer_class=CountrySerializer; permission_classes=[permissions.AllowAny]
class RegionViewSet(viewsets.ReadOnlyModelViewSet): queryset=Region.objects.select_related('country'); serializer_class=RegionSerializer; permission_classes=[permissions.AllowAny]; filterset_fields=['country__code']
class CityViewSet(viewsets.ReadOnlyModelViewSet): queryset=City.objects.select_related('region__country'); serializer_class=CitySerializer; permission_classes=[permissions.AllowAny]; filterset_fields=['region__code','region__country__code']; search_fields=['name']
class FuelTypeViewSet(viewsets.ReadOnlyModelViewSet): queryset=FuelType.objects.all(); serializer_class=FuelTypeSerializer; permission_classes=[permissions.AllowAny]
class StationViewSet(viewsets.ModelViewSet):
    queryset=Station.objects.select_related('city__region__country').filter(is_active=True); serializer_class=StationSerializer
    filterset_fields=['city','city__region__code','city__region__country__code','brand']; search_fields=['name','brand','address','postal_code']; ordering_fields=['name','brand']
    def perform_create(self,serializer): serializer.save(created_by=self.request.user)
    @action(detail=False,methods=['get'],permission_classes=[permissions.AllowAny])
    def nearby(self,request):
        try: lat=float(request.query_params['lat']); lon=float(request.query_params['lon']); radius=float(request.query_params.get('radius',10))
        except (KeyError,ValueError): return Response({'detail':'Use ?lat=45.5&lon=-73.6&radius=10'},status=400)
        found=[]
        for s in self.get_queryset():
            d=distance_km(lat,lon,s.latitude,s.longitude)
            if d<=radius: found.append((d,s))
        found.sort(key=lambda x:x[0]); data=[]
        for d,s in found[:50]:
            row=StationSerializer(s,context={'request':request}).data; row['distance_km']=round(d,2); data.append(row)
        return Response(data)

class PriceSubmissionViewSet(viewsets.ModelViewSet):
    queryset=PriceSubmission.objects.select_related('station','fuel_type','submitted_by'); serializer_class=PriceSubmissionSerializer
    filterset_fields=['station','fuel_type__code','status']; ordering_fields=['price','submitted_at']
    def perform_create(self,serializer): serializer.save(submitted_by=self.request.user,status='pending')
    @action(detail=True,methods=['post'])
    def vote(self,request,pk=None):
        sub=self.get_object()
        try: value=int(request.data.get('value'))
        except (TypeError,ValueError): return Response({'detail':'value must be 1 or -1'},status=400)
        if value not in (1,-1): return Response({'detail':'value must be 1 or -1'},status=400)
        PriceVote.objects.update_or_create(submission=sub,user=request.user,defaults={'value':value})
        sub.upvotes=sub.votes.filter(value=1).count(); sub.downvotes=sub.votes.filter(value=-1).count()
        if sub.upvotes>=2 and sub.upvotes>=sub.downvotes+2: sub.status='verified'
        sub.save(update_fields=['upvotes','downvotes','status'])
        return Response(PriceSubmissionSerializer(sub).data)

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class=FavoriteSerializer
    def get_queryset(self): return Favorite.objects.filter(user=self.request.user).select_related('station__city__region__country')
    def perform_create(self,serializer): serializer.save(user=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def analytics(request):
    qs=PriceSubmission.objects.filter(status='verified')
    city=request.query_params.get('city'); fuel=request.query_params.get('fuel_type')
    if city: qs=qs.filter(station__city__name__iexact=city)
    if fuel: qs=qs.filter(fuel_type__code=fuel)
    return Response({'verified_submissions':qs.count(),'average_price':qs.aggregate(v=Avg('price'))['v']})
