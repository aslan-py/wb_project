from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.models import MyUser
from users.schema import (
    add_balance_schema,
    login_schema,
    profile_schema,
    refresh_schema,
    register_schema,
)
from users.serializers import (
    AddToBalanceSerializer,
    RegistrationSerializer,
    UpdateProfileSerializer,
)
from users.services import top_up_balance


@register_schema
class RegisterView(CreateAPIView):
    """Регистрация нового пользователя."""

    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)


@login_schema
class LoginView(TokenObtainPairView):
    """Авторизация: выдаёт пару JWT-токенов."""


@refresh_schema
class RefreshView(TokenRefreshView):
    """Обновление access-токена по refresh-токену."""


@profile_schema
class ProfileView(RetrieveUpdateAPIView):
    """Профиль текущего пользователя: просмотр и редактирование."""

    serializer_class = UpdateProfileSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = (
        'get',
        'patch',
    )

    def get_object(self) -> MyUser:
        """Возвращает текущего пользователя из запроса."""
        return self.request.user


@add_balance_schema
class AddBalanceView(APIView):
    """Пополнение баланса текущего пользователя."""

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        """Принимает сумму, пополняет баланс, возвращает новый баланс."""
        serializer = AddToBalanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = top_up_balance(
            request.user, serializer.validated_data['amount']
        )
        return Response({'balance': user.balance})
