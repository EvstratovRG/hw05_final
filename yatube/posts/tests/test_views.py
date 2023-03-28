from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, Group, Comment
from posts.forms import PostForm

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.second_page_posts_count = settings.POSTS_QUANTITY // 2
        cls.total_posts_count = (
            settings.POSTS_QUANTITY
            + cls.second_page_posts_count
        )
        cls.user = User.objects.create_user(username='username')
        cls.group = Group.objects.create(
            title='Test_group',
            slug='Test-group',
            description='Test-group-description',
        )
        cls.post = Post.objects.bulk_create(
            [Post(author=cls.user,
                  text=f'Test Text {i}',
                  group=cls.group,
                  )for i in range(cls.total_posts_count)])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_first_page_posts(self):
        paginate_pages = [
            "/",
            f"/group/{self.group.slug}/",
            f"/profile/{self.user}/",
        ]
        for url in paginate_pages:
            with self.subTest(url):
                response = self.client.get(url)
                self.assertEqual(len(
                    response.context['page_obj']), settings.POSTS_QUANTITY)

    def test_second_page_posts(self):
        paginate_pages = [
            "/",
            f"/group/{self.group.slug}/",
            f"/profile/{self.user}/",
        ]
        for url in paginate_pages:
            with self.subTest(url):
                response = self.client.get(f"{url}?page=2")
                self.assertEqual(len(
                    response.context['page_obj']),
                    self.second_page_posts_count)


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='username')
        cls.group = Group.objects.create(
            title='Test_group',
            slug='Test-group',
            description='Test-group-description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test_Text',
            group=cls.group)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
            'posts/profile.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
            'posts/create_post.html',
        }
        for address, template in templates_pages_names.items():
            with self.subTest(reverse_name=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)
        self.assertEqual(response.context['group'].slug, self.group.slug)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.context['author'], self.post.author)
        self.assertEqual(response.context['page_obj'][0], self.post)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context['posts'].text, self.post.text)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_edit_post_show_correct_context(self):
        """Шаблон create_post(edit) сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', args=[self.post.id]))
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertEqual(response.context['form'].instance, self.post)

    def test_create_post_check_with_group(self):
        """Пользователь не может создавать новые посты в группе,
          к которой он не принадлежит"""
        other_group = Group.objects.create(
            title='Other Group',
            slug='other-group',
            description='Other description')
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': other_group.slug}))
        self.assertNotContains(response, 'new post')


class PostCommentsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='comment_username')
        cls.post = Post.objects.create(
            author=cls.user,
            text='test post',
        )
        cls.text_comment = 'test comment'

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_add_only_authorized(self):
        '''Комментировать посты может только авторизованный пользователь.'''
        text_comment = 'test Comment'
        response = self.authorized_client.post(reverse(
            'posts:add_comment',
            args=[self.post.id]),
            data={'text': text_comment},
            follow=True
        )
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.text, text_comment)
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.post.author)
        self.assertRedirects(
            response, f'/posts/{self.post.id}/'
        )
