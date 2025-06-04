from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author():
    """Создает пользователя-автора комментария."""
    return User.objects.create(username='Автор комментария')


@pytest.fixture
def author_client(author):
    """Создает авторизованный клиент для автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader():
    """Создает пользователя-читателя (не автора)."""
    return User.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader):
    """Создает авторизованный клиент для читателя."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    """Создает тестовую новость."""
    return News.objects.create(title='Заголовок', text='Текст новости')


@pytest.fixture
def comment(author, news):
    """Создает тестовый комментарий к новости."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def multiple_news():
    """Создает новости с разными датами для тестирования."""
    today = datetime.today()
    news_count = settings.NEWS_COUNT_ON_HOME_PAGE + 1
    return [
        News.objects.create(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(news_count)
    ]


@pytest.fixture
def multiple_comments(news, author):
    """Создает несколько комментариев с разными датами."""
    now = datetime.now()
    for index in range(5):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {index}'
        )
        comment.created = now + timedelta(hours=index)
        comment.save()


@pytest.fixture
def home_url():
    """URL главной страницы."""
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    """URL страницы новости."""
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def comment_edit_url(comment):
    """URL редактирования комментария."""
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def comment_delete_url(comment):
    """URL удаления комментария."""
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def login_url():
    """URL страницы входа."""
    return reverse('users:login')


@pytest.fixture
def logout_url():
    """URL выхода из системы."""
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    """URL страницы регистрации."""
    return reverse('users:signup')
