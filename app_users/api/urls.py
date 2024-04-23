from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app_users.api.views import (
    UserViewSet,
    CustomAuthToken,
    CustomJWTPairToken,
    CustomJWTPairRefresh,
    CustomJWTTokenVerify,
)

router = DefaultRouter(trailing_slash=False)
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("api-token-auth/", CustomAuthToken.as_view(), name="api_token_auth"),
    path("api/token/", CustomJWTPairToken.as_view(), name="token_obtain_pair"),
    path(
        "api/token/refresh/",
        CustomJWTPairRefresh.as_view(),
        name="token_refresh",
    ),
    path(
        "api/token/verify/",
        CustomJWTTokenVerify.as_view(),
        name="token_verify",
    ),
]
