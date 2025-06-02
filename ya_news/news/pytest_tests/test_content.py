import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_news_count(client, multiple_news):
    """Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == 10


def test_news_order(client, multiple_news):
    """Новости отсортированы от самой свежей к самой старой."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, multiple_comments):
    """Комментарии отсортированы от старых к новым."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_form(client, news):
    """Анонимному пользователю недоступна форма комментария."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_clien(author_client, news):
    """Авторизованному пользователю доступна форма комментария."""
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert response.context['form'] is not None
