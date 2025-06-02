import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_home_page_availability(client):
    """Главная страница доступна анонимному пользователю."""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == 200


def test_news_detail_availability(client, news):
    """Страница отдельной новости доступна анонимному пользователю."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert response.status_code == 200


def test_comment_edit_delete_availability(author_client, comment):
    """Страницы удаления и редактирования доступны автору комментария."""
    urls = [
        reverse('news:edit', args=(comment.pk,)),
        reverse('news:delete', args=(comment.pk,)),
    ]
    for url in urls:
        response = author_client.get(url)
        assert response.status_code == 200


def test_anonymous_redirect_to_login(client, comment):
    """Аноним перенаправляется на страницу авторизации."""
    login_url = reverse('users:login')
    urls = [
        reverse('news:edit', args=(comment.pk,)),
        reverse('news:delete', args=(comment.pk,)),
    ]
    for url in urls:
        redirect_url = f'{login_url}?next={url}'
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == redirect_url


def test_reader_cant_edit_delete_comment(reader_client, comment):
    """Чужой пользователь не может редактировать/удалять комментарии."""
    urls = [
        reverse('news:edit', args=(comment.pk,)),
        reverse('news:delete', args=(comment.pk,)),
    ]
    for url in urls:
        response = reader_client.get(url)
        assert response.status_code == 404


def test_auth_pages_availability(client):
    """Страницы регистрации, входа и выхода доступны анонимам."""
    urls = [
        reverse('users:login'),
        reverse('users:signup'),
    ]
    for url in urls:
        response = client.get(url)
        assert response.status_code == 200

    response = client.post(reverse('users:logout'))
    assert response.status_code == 200
