from datetime import datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author():
    """Создает пользователя-автора комментария."""
    return User.objects.create(username='Автор комментария')


@pytest.fixture
def author_client(author, client):
    """Создает авторизованный клиент для автора."""
    client.force_login(author)
    return client


@pytest.fixture
def reader():
    """Создает пользователя-читателя (не автора)."""
    return User.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader, client):
    """Создает авторизованный клиент для читателя."""
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
    """Создает 11 новостей с разными датами для тестирования."""
    today = datetime.today()
    return [
        News.objects.create(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(11)
    ]


@pytest.fixture
def multiple_comments(news, author):
    """Создает несколько комментариев с разными датами."""
    now = datetime.now()
    return [
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {index}',
            created=now + timedelta(hours=index)
        )
        for index in range(5)
    ]
