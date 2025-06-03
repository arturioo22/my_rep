import pytest

from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, multiple_news, home_url):
    """Количество новостей на главной странице."""
    response = client.get(home_url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, multiple_news, home_url):
    """Новости отсортированы от самой свежей к самой старой."""
    response = client.get(home_url)
    news_dates = [news.date for news in response.context['object_list']]
    assert news_dates == sorted(news_dates, reverse=True)


def test_comments_order(client, news, multiple_comments, detail_url):
    """Комментарии отсортированы от старых к новым."""
    response = client.get(detail_url)
    assert 'news' in response.context
    comments = response.context['news'].comment_set.all()
    comments_times = [comment.created for comment in comments]
    assert comments_times == sorted(comments_times)


def test_anonymous_form(client, news, detail_url):
    """Анонимному пользователю недоступна форма комментария."""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_form(author_client, news, detail_url):
    """Авторизованному пользователю доступна форма комментария."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
