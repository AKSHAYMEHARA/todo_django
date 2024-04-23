from django.contrib.auth import authenticate
from django.utils import timezone

# From drf and drf-jwt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer,
    TokenVerifySerializer,
)

# From system app
from app_users.models import AppUser
from app_users.api import (
    signals,
)  # This one is intentionlly imported to trigger signals
from app_users.api.permissions import CustomIsOwnerOrIsAdmin
from app_users.api.serializers import (
    AppUserSerializers,
    CustomTokenObtainPairSerializer,
)


"""
1. Anyone can register himself -> AllowAny
2. Only user can r,u himself -> IsOwner
3. Admin can crud others -> IsAdmin
"""


class UserViewSet(ModelViewSet):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializers

    def get_permissions(self):
        if self.action in ["list"]:
            permission_classes = [IsAuthenticated, IsAdminUser]

        elif self.action in ["create"]:
            permission_classes = [AllowAny]

        elif self.action in ["retrieve", "update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, CustomIsOwnerOrIsAdmin]

        elif self.action in ["destroy"]:
            permission_classes = [IsAuthenticated, IsAdminUser]

        else:
            permission_classes = [IsAuthenticated, IsAdminUser]

        result = [permission() for permission in permission_classes]
        return result

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "success": True,
                    "data": serializer.data,
                    "message": "Users Fetched Successfully",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "data": [],
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance=instance)
            return Response(
                {
                    "success": True,
                    "data": [serializer.data],
                    "message": "User Fetched Successfully",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "data": [],
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=self.request.data)
            if serializer.is_valid():
                user = serializer.save(last_login=timezone.now())
                token_serializer = CustomTokenObtainPairSerializer(
                    data=self.request.data
                )

                if token_serializer.is_valid():
                    return Response(
                        {
                            "success": True,
                            "data": {
                                **serializer.data,
                                **token_serializer.validated_data,
                            },
                            "message": "User Created Successfully",
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {
                            "success": False,
                            "data": [],
                            "message": token_serializer.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {
                        "success": False,
                        "data": [],
                        "message": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "data": [],
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(
                instance=self.get_object(), data=self.request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "data": serializer.data,
                        "message": "User Updated Successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "success": False,
                        "data": [],
                        "message": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "data": [],
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            self.perform_destroy(self.get_object())
            return Response(
                {
                    "success": True,
                    "data": [],
                    "message": "User Deleted Successfully",
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "data": [],
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "success": True,
                    "data": [
                        {
                            "token": token.key,
                            "userId": user.pk,
                            "email": user.email,
                            "username": user.username,
                            "isAdmin": user.is_superuser,
                        }
                    ],
                    "message": "User Logged In Successfully",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "data": [],
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomJWTPairToken(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            user = authenticate(
                email=self.request.data["email"], password=self.request.data["password"]
            )
            print("🚀 ~ user:", user)
            serializer = self.serializer_class(data=self.request.data)
            user_serializer = AppUserSerializers(user, many=False)

            if user is not None and serializer.is_valid():
                return Response(
                    {
                        "success": True,
                        "data": {**serializer.validated_data, **user_serializer.data},
                        "message": "Token Generated Successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "success": False,
                        "data": [],
                        "message": "Invalid Creds OR No Active User",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "data": [],
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomJWTPairRefresh(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=self.request.data)

            if serializer.is_valid():
                return Response(
                    {
                        "success": True,
                        "data": [serializer.validated_data],
                        "message": "Access Token Generated Successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "success": False,
                        "data": [],
                        "message": "Access Token Generation Failed",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "data": [],
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomJWTTokenVerify(TokenVerifyView):
    serializer_class = TokenVerifySerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=self.request.data)

            if serializer.is_valid():
                return Response(
                    {
                        "success": True,
                        "data": [],
                        "message": "Token Verified Successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "success": False,
                        "data": [],
                        "message": "Access Token Verification Failed",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "data": [],
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
