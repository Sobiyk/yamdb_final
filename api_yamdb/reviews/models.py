from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import year_validator
from users.models import User


class Category(models.Model):
    """Модель категории"""
    name = models.CharField(max_length=256, verbose_name='Название категории')
    slug = models.SlugField(max_length=50,
                            unique=True,
                            verbose_name='slug категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('id',)

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    """Модель жанра"""
    name = models.CharField(max_length=256, verbose_name='Название жанра')
    slug = models.SlugField(max_length=50,
                            unique=True,
                            verbose_name='slug жанра')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('id',)

    def __str__(self) -> str:
        return self.name


class Title(models.Model):
    """Модель произведения"""
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        related_name='titles',
        db_index=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        related_name='titles',
        db_index=True
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        db_index=True
    )
    description = models.TextField('Описание')
    year = models.PositiveSmallIntegerField(
        'Год создания',
        db_index=True,
        validators=[year_validator]
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('id',)

    def __str__(self) -> str:
        return self.name


class Review(models.Model):
    """Модель для Отзыва+рейтинг."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name="Произведение",
        related_name="reviews",
    )
    text = models.TextField("Текст отзыва")
    score = models.PositiveSmallIntegerField(
        verbose_name="Оценка",
        default=1,
        validators=[
            MinValueValidator(1, 'Доступны оценки в диапазоне от 1 до 10'),
            MaxValueValidator(10, 'Доступны оценки в диапазоне от 1 до 10')
        ],
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        verbose_name = "Ревью"
        verbose_name_plural = "Ревью"
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                name="unique_review", fields=["author", "title"]
            ),
        ]

    def __str__(self):
        return self.text[:30]


class Comment(models.Model):
    """Модель для Комментария к Отзыву."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField("Текст комментария")
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("id",)

    def __str__(self):
        return self.text[:30]
