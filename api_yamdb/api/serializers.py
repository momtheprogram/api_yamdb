from django.db.models import Avg
from rest_framework.serializers import (
    CharField,
    EmailField,
    ModelSerializer,
    RegexField,
    Serializer,
    SerializerMethodField,
    SlugRelatedField,
    ValidationError,
)

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class UserSerializer(ModelSerializer):
    """ Сериализатор для юзера."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'bio'
        )

    def validate_username(self, username):
        if username.lower() == 'me':
            raise ValidationError('You can not use "me"!')
        return username


class SignUpSerializer(Serializer):
    """Сериалайзер для регистрации."""
    username = RegexField(max_length=150, regex=r'^[\w.@+-]+')
    email = EmailField(max_length=254)

    class Meta:
        fields = ("username", "email")

    def validate(self, attrs):
        username = attrs.get('username')
        if username.lower() == 'me':
            raise ValidationError('Нельзя использовать me')
        return attrs


class TokenSerializer(Serializer):
    """Сериалайзер JWT токена."""
    username = CharField(required=True)
    confirmation_code = CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class ReviewSerializer(ModelSerializer):
    """Сериализатор отзывов."""
    author = SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        read_only_fields = ('id', 'title', 'pub_date')
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, attrs):
        is_exist = Review.objects.filter(
            author=self.context['request'].user,
            title=self.context['view'].kwargs.get('title_id')).exists()
        if is_exist and self.context['request'].method == 'POST':
            raise ValidationError(
                'Пользователь уже оставлял отзыв на это произведение'
            )
        return attrs


class CommentSerializer(ModelSerializer):
    """Сериализатор комментариев."""
    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('id', 'review', )


class GenreSerializer(ModelSerializer):
    """Сериализатор жанров"""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(ModelSerializer):
    """Сериализатор категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GetTitleSerializer(ModelSerializer):
    """Сериализатор получения произведений"""
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = ('rating', 'category', 'genre')

    def get_rating(self, obj):
        rating = obj.reviews.all().aggregate(Avg('score'))['score__avg']
        if rating:
            return round(rating)
        else:
            return None


class PostTitleSerializer(ModelSerializer):
    """Сериализатор создания произведений"""
    genre = SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=False
    )
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Title
        fields = '__all__'
