from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, Group


User = get_user_model()


class PostIndexTestCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='username')
        cls.group = Group.objects.create(
            title='Test_group',
            slug='Test-group',
            description='Test-group-description'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test_Text',
            group=cls.group
        )

    def setUp(self):
        cache.clear()

    def test_displayed_posts(self):
        '''Отображение тестовых сообщений из кэша.'''
        response = self.client.get(reverse('posts:index'))
        self.assertContains(
            response, self.post.text, status_code=HTTPStatus.OK)
        Post.objects.all().delete()
        response = self.client.get(reverse('posts:index'))
        self.assertContains(
            response, self.post.text, status_code=HTTPStatus.OK)
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotContains(
            response, self.post.text, status_code=HTTPStatus.OK)
