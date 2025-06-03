from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Общие тестовые данные."""
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Другой пользователь')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)


class TestRoutes(BaseTestCase):
    """Тестирование маршрутов."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            author=cls.author,
            slug='test-note'
        )

        cls.urls = {
            'home': reverse('notes:home'),
            'login': reverse('users:login'),
            'signup': reverse('users:signup'),
            'list': reverse('notes:list'),
            'success': reverse('notes:success'),
            'add': reverse('notes:add'),
            'detail': reverse('notes:detail', args=(cls.note.slug,)),
            'edit': reverse('notes:edit', args=(cls.note.slug,)),
            'delete': reverse('notes:delete', args=(cls.note.slug,)),
        }
        cls.login_url = cls.urls['login']

    def test_availability_anonymous(self):
        """Проверка доступности страниц анонимному пользователю."""
        public_urls = (
            self.urls['home'],
            self.urls['login'],
            self.urls['signup'],
        )
        for url in public_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_auth_user(self):
        """Проверка доступности страниц аутентифицированному пользователю."""
        auth_urls = (
            self.urls['list'],
            self.urls['success'],
            self.urls['add'],
        )
        for url in auth_urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_actions(self):
        """Страницы заметки доступны только автору."""
        action_urls = (
            self.urls['detail'],
            self.urls['edit'],
            self.urls['delete'],
        )

        for url in action_urls:
            with self.subTest(user='author', url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        for url in action_urls:
            with self.subTest(user='reader', url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_anonymous(self):
        """Анонимный пользователь перенаправляется на страницу логина."""
        private_urls = (
            self.urls['list'],
            self.urls['success'],
            self.urls['add'],
            self.urls['detail'],
            self.urls['edit'],
            self.urls['delete'],
        )
        for url in private_urls:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
