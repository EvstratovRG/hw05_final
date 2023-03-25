from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.group = Group.objects.create(
            title='Test_group',
            slug='Test-group',
            description='Test-group-description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test_post',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_client_urls_HTTP_OK(self):
        templates = [
            "/",
            f"/group/{self.group.slug}/",
            f"/profile/{self.user}/",
            f"/posts/{self.post.id}/",
        ]
        for status in templates:
            with self.subTest(status):
                response = self.guest_client.get(status)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_client_post_create_status_200(self):
        """Страница /create/ доступна авторизованному пользоваелю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_client_redirect_from_create_post_302(self):
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_guest_client_redirect_from_edit_post_302(self):
        response = self.guest_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_accessible_by_author(self):
        """Страница /create/edit доступна автору поста."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_accessible_not_by_author(self):
        """Страница /create/edit недоступна не автору поста."""
        not_author = User.objects.create(username='not_author')
        self.authorized_client = Client()
        self.authorized_client.force_login(not_author)
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/', follow=True)
        self.assertRedirects(
            response, f'/posts/{self.post.id}/')

    def test_not_exists_page_return_404(self):
        """404"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """Проверка шаблонов."""
        templates_url_names = [
            ('posts/index.html', '/'),
            ('posts/group_list.html', f'/group/{self.group.slug}/'),
            ('posts/profile.html', f'/profile/{self.user}/'),
            ('posts/post_detail.html', f'/posts/{self.post.id}/'),
            ('posts/create_post.html', f'/posts/{self.post.id}/edit/'),
        ]
        for template, url in templates_url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
