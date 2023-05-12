import uuid

from api.filters import TitleFilter
from api.mixins import BaseListCreateDestroyView
from api.permissions import (AuthorAndStaffOrReadOnly, IsAdminOrReadOnly,
                             OwnerOrAdmins)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             SignUpSerializer, TitleReadSerializer,
                             TitleWriteSerializer, TokenSerializer,
                             UsersSerializer)
from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title
from users.models import User


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_post(request):
    """Функция регистрации новых пользователей."""
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    username = serializer.validated_data['username']
    try:
        user, create = User.objects.get_or_create(
            username=username,
            email=email
        )
    except IntegrityError:
        return Response(
            'Такой логин или email уже существуют',
            status=status.HTTP_400_BAD_REQUEST
        )
    confirmation_code = str(uuid.uuid4())
    user.confirmation_code = confirmation_code
    user.save()
    send_mail(
        'Код подверждения', confirmation_code,
        settings.DEFAULT_FROM_EMAIL, (email, ), fail_silently=False
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_post(request):
    """Функция получения токена при регистрации."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    user_base = get_object_or_404(User, username=username)
    if confirmation_code == user_base.confirmation_code:
        token = str(AccessToken.for_user(user_base))
        return Response({'token': token}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('pk')
    serializer_class = UsersSerializer
    pagination_class = PageNumberPagination
    permission_classes = (OwnerOrAdmins, )
    filter_backends = (filters.SearchFilter, )
    http_method_names = ['get', 'post', 'patch', 'delete']
    filterset_fields = ('username')
    search_fields = ('username', )
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        user = self.request.user
        if request.method == 'GET':
            serializer = UsersSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UsersSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('role'):
            serializer.validated_data.pop('role')
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    """
    Получить список всех произведений.
    Добавление нового произведения.
    Получение произведения по id.
    Обновление произведения по id.
    Удаление произведения.
    """
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_rating(self, title):
        return title.reviews.all().aggregate(rating=Avg('score'))['rating']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        title = self.get_object()
        response.data['rating'] = self.get_rating(title)
        return response

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        for title in response.data['results']:
            obj = get_object_or_404(Title, pk=title['id'])
            title['rating'] = self.get_rating(obj)
        return response


class CategoryViewSet(BaseListCreateDestroyView):
    """
    Получить список всех категорий.
    Добавление новой категории.
    Удаление категории по полю slug.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)


class GenreViewSet(BaseListCreateDestroyView):
    """
    Получить список всех жанров.
    Добавление нового жанра.
    Удаление жанра по полю slug.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)


class ReviewViewSet(ModelViewSet):
    """
    Получить список всех отзывов.
    Добавление нового отзыва.
    Получение отзыва по id.
    Обновление отзыва по id.
    Удаление отзыва.
    """

    serializer_class = ReviewSerializer
    permission_classes = (AuthorAndStaffOrReadOnly,)
    http_method_names = ("get", "post", "delete", "patch")

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(ModelViewSet):
    """
    Получить список всех комментариев.
    Добавление нового комментария к отзыву.
    Получить комментарий по id.
    Обновление комментария по id.
    Удаление комментария.
    """

    serializer_class = CommentSerializer
    permission_classes = (AuthorAndStaffOrReadOnly,)
    http_method_names = ("get", "post", "delete", "patch")

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get("review_id"),
            title_id=self.kwargs.get("title_id"),
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
