from django.db.models import Max
from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly,)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from users.models import User
from .permissions import (
    IsAdmin, IsSuperuser, IsAdminOrReadOnly, IsAuthor, IsModerator,
)
from .utils import (
    generate_confirmation_code,
    send_mail_to_user,
    BaseViewSet,
)
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    GetTitleSerializer,
    PostTitleSerializer,
    UserSerializer,
    ReviewSerializer,
    CommentSerializer,
)
from reviews.models import Category, Genre, Title, Comment, Review


class RegisterView(APIView):
    """
    Получает email, возвращает код доступа
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email)
        if len(user) > 0:
            confirmation_code = user[0].confirmation_code
        else:
            confirmation_code = generate_confirmation_code()
            max_id = User.objects.aggregate(Max('id'))['id__max'] + 1
            data = {'email': email, 'confirmation_code': confirmation_code,
                    'username': f'User {max_id}'}
            serializer = UserSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        send_mail_to_user(email, confirmation_code)
        return Response({'email': email})


class TokenView(APIView):
    """
    Получает email и confirmation_code, возвращает токен
    """
    permission_classes = (AllowAny,)

    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def post(self, request):
        user = get_object_or_404(User, email=request.data.get('email'))
        if user.confirmation_code != request.data.get('confirmation_code'):
            response = {'confirmation_code': 'Неверный код'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response = {'token': self.get_token(user)}
        return Response(response, status=status.HTTP_200_OK)


class UsersViewSet(ModelViewSet):
    """
    Вьюсет для работы с пользователями
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    permission_classes = (IsAuthenticated, IsSuperuser | IsAdmin,)

    @action(
        detail=False, permission_classes=(IsAuthenticated,),
        serializer_class=(UserSerializer,), methods=['get', 'patch'],
        url_path='me'
    )
    def get_or_update_self(self, request):
        if request.method != 'GET':
            serializer = self.get_serializer(
                instance=request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(request.user, many=False)
            return Response(serializer.data)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'genre', 'category',)

    def get_serializer_class(self):
        """Выбор сериализатора по типу запроса"""
        if self.action in ('POST', 'PUT', 'PATCH'):
            return PostTitleSerializer
        return GetTitleSerializer


class GenreViewSet(BaseViewSet):
    """Вьюсет для жанров"""
    queryset = Genre.objects.all()
    serializer_class = CategorySerializer


class CategoryViewSet(BaseViewSet):
    """Вьюсет для категорий"""
    queryset = Category.objects.all()
    serializer_class = GenreSerializer


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor | IsModerator |
                          IsAdminOrReadOnly | IsSuperuser]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(
            Review.objects.filter(title_id=title_id), pk=review_id
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(
            Review.objects.filter(title_id=title_id), pk=review_id
        )
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor | IsModerator |
                          IsAdminOrReadOnly | IsSuperuser]
    # pagination_class = PageNumberPagination

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all().order_by('id')

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)
