from rest_framework.serializers import ModelSerializer
from app_users.models import AppUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class AppUserSerializers(ModelSerializer):
    class Meta:
        model = AppUser
        exclude = ["user_permissions", "groups"]
        extra_kwargs = {
            "password": {"write_only": True},
            "is_superuser": {"read_only": True},
            "is_staff": {"read_only": True},
            "is_active": {"read_only": True},
            "date_joined": {"read_only": True},
        }

    def create(self, validated_data, **kwargs):
        password = validated_data.pop("password")  # Remove password from validated_data
        user = AppUser.objects.create(**validated_data)
        user.set_password(password)  # Set the password separately
        user.save(**kwargs)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# This will add other info into token payload
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["username"] = user.username
        # token["firstname"] = user.first_name
        token["isAdmin"] = user.is_superuser
        return token
