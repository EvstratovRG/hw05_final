from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

from .validators import validate_not_empty

from core.models import CreatedModel


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=settings.MAXIMUM_FIELD_LENGTH)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=settings.MAXIMUM_FIELD_LENGTH)

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        validators=[validate_not_empty],
        help_text='Write your post here.')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        help_text='Publication date.')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text='Choose the group.'
    )
    image = models.ImageField(
        'image', upload_to='posts/',
        blank=True,
        help_text='Download the image.'
    )
    likes = models.ManyToManyField(
        User,
        related_name='blog_posts'
    )

    class Meta:
        ordering = ("-pub_date",)

    def total_post_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.text[:settings.SYMBOLS_SLICE]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='Вы можете написать комментарий.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments')
    text = models.TextField(
        max_length=settings.MAXIMUM_FIELD_LENGTH,
        validators=[validate_not_empty],
        help_text='Напишите Ваш комментарий.')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='User'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Author'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_author_user_following'
            )
        ]
