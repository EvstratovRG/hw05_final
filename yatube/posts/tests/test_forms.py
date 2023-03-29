import tempfile
import shutil

from http import HTTPStatus

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Group, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author = User.objects.create(username='username')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug',
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Test post',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = PostFormTests.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_images_in_context(self):
        """При выводе поста с картинкой изображение передаётся в context."""

    def test_create_valid_form_post(self):
        """Валидная форма create_post создает запись."""
        posts_count = Post.objects.count()
        picture = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='picture.png',
            content=picture,
            content_type='image/png'
        )
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': PostFormTests.author})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image='posts/picture.png'
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_unauthorized(self):
        """Неавторизованный пользователь не может создать пост."""
        posts_count = Post.objects.count()
        form_data = {"text": "test_text"}
        response = self.guest_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=%2Fcreate%2F')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(Post.objects.filter(text=form_data["text"]).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_form_post(self):
        """Валидная форма post_edit изменяет запись в Post."""
        group = Group.objects.create(
            title="test group",
            slug="test-slug",
            description="test description",
        )
        form_data = {"text": "change_text", "group": group.id}
        post = Post.objects.create(
            author=self.user,
            text=form_data.values,
        )
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=({post.id})),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse(
                "posts:post_detail", kwargs={"post_id": post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(text=form_data['text']).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_guest_client(self):
        """Пользователь, не может изменить пост,
        автором которого он не является."""
        posts_count = Post.objects.count()
        group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        form_data = {"text": "Изменяем текст", "group": group.id}
        post = Post.objects.create(
            author=self.user,
            text="Тестовый текст",
        )
        response = self.guest_client.post(
            reverse("posts:post_edit", args=({post.id})),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, f"/auth/login/?next=/posts/{post.id}/edit/")
        self.assertNotEqual(Post.objects.count(), posts_count)
        self.assertFalse(Post.objects.filter(text=form_data['text']).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)
