from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User
from users.validators import UsernameValidator


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    username_validator = UsernameValidator()
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[username_validator],
    )

    def validate(self, data):
        if data['username'].lower() == 'me':
            raise serializers.ValidationError('Логин me не доступен')
        return data

    class Meta:
        fields = ('username', 'email')


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели категории."""

    class Meta:
        model = Category
        exclude = ('id', )


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели жанра."""

    class Meta:
        model = Genre
        exclude = ('id', )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи модели произведения."""
    genre = serializers.SlugRelatedField(slug_field='slug',
                                         queryset=Genre.objects.all(),
                                         many=True)
    description = serializers.CharField(required=False)
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения модели произведения."""
    rating = serializers.ReadOnlyField()
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ревью."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date")
        model = Review

    def validate(self, data):
        """Запрещает пользователям писать второе ревью на произведение."""
        request = self.context.get("request")
        title_id = self.context.get("view").kwargs.get("title_id")
        if (
            request.method == "POST"
            and Review.objects.filter(
                author=request.user, title__id=title_id
            ).exists()
        ):
            raise serializers.ValidationError(
                "Писать второе ревью нельзя."
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментария."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        fields = ("id", "author", "review", "text", "pub_date")
        read_only_fields = ("review",)
        model = Comment
