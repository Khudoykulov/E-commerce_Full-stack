from rest_framework import generics, status, viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated

from apps.account.models import User, UserToken, Banner
from apps.account.serializers import (
    UserRegisterSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    SuperUserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
    UserDeleteSerializer,
    UserProfileFullSerializer,
    PasswordChangeSerializer,
    NewBlockSerializer,
    AdviceSerializer,
    CallSerializer,
    BannerSerializer,
    CartaSerializer,
    UserLocationSerializer,
)
from .permissions import IsOwnerOrReadOnly
from .models import UserLocation, NewBlock, Advice, Call, Carta
from apps.product.permissions import IsAdminOrReadOnly


class UserLocationUpdateAPIView(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    serializer_class = UserLocationSerializer
    # parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]  # Faqat ro'yxatdan o'tgan foydalanuvchilarga ruxsat

    def get_queryset(self):
        # Faqat hozirgi foydalanuvchining lokatsiyasi ustida ishlash uchun
        return UserLocation.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted': True}, status=status.HTTP_200_OK)


class UserRegisterView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = UserToken.objects.create(user=user)
        # ecommerce_send_email.apply_async(("Activation Token Code", str(token.token), [user.phone]), )
        data = {
            'success': True,
            'detail': 'Activation Token Code has been sent to your phone.',
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserProfileSerializer
    queryset = User.objects.filter(is_active=True)
    permission_classes = [IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        data = {
            'success': True,
            'detail': 'Your account has been deactivated.',
        }
        return Response(data, status=status.HTTP_200_OK)


class SuperUserCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = SuperUserCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = SuperUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Superuser muvaffaqiyatli yaratildi"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = UserProfileFullSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserUpdateSerializer,
        responses=UserProfileFullSerializer
    )
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Yangilangan to'liq profil ma'lumotlarini qaytarish
            return Response(UserProfileFullSerializer(user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Yangilangan to'liq profil ma'lumotlarini qaytarish
            return Response(UserProfileFullSerializer(user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserDeleteSerializer,
        responses={status.HTTP_204_NO_CONTENT: "User successfully deleted"}
    )
    def post(self, request, *args, **kwargs):
        serializer = UserDeleteSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    """Parolni o'zgartirish"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PasswordChangeSerializer,
        responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}}
    )
    def post(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Parol muvaffaqiyatli o'zgartirildi"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewBlockListCreateView(generics.ListCreateAPIView):
    queryset = NewBlock.objects.all()
    serializer_class = NewBlockSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]


class NewBlockDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NewBlock.objects.all()
    serializer_class = NewBlockSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]


class AdviceViewSet(viewsets.ModelViewSet):
    queryset = Advice.objects.all()
    permission_classes = [permissions.AllowAny]  # Public endpoint
    serializer_class = AdviceSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted': True}, status=status.HTTP_200_OK)


class CallViewSet(viewsets.ModelViewSet):
    queryset = Call.objects.all()
    permission_classes = [permissions.AllowAny]  # Public endpoint
    serializer_class = CallSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted': True}, status=status.HTTP_200_OK)


class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint
    parser_classes = [MultiPartParser, FormParser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted': True}, status=status.HTTP_200_OK)


class CartaViewSet(viewsets.ModelViewSet):
    queryset = Carta.objects.all()
    serializer_class = CartaSerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint
