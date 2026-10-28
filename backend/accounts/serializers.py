from rest_framework import serializers
from .models import User
class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,min_length=8)
    class Meta: model=User; fields=('id','email','username','password','first_name','last_name','country_code')
    def create(self, validated_data): return User.objects.create_user(**validated_data)
class UserSerializer(serializers.ModelSerializer):
    class Meta: model=User; fields=('id','email','username','first_name','last_name','reputation','country_code'); read_only_fields=('reputation',)
