from http import HTTPStatus

import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_name, user_role, expected_status',
    [
        ('home_url', 'anonymous', HTTPStatus.OK),
        ('detail_url', 'anonymous', HTTPStatus.OK),
        ('login_url', 'anonymous', HTTPStatus.OK),
        ('signup_url', 'anonymous', HTTPStatus.OK),
        ('comment_edit_url', 'author', HTTPStatus.OK),
        ('comment_delete_url', 'author', HTTPStatus.OK),
        ('comment_edit_url', 'reader', HTTPStatus.NOT_FOUND),
        ('comment_delete_url', 'reader', HTTPStatus.NOT_FOUND),
    ],
    ids=[
        'home-anonymous',
        'detail-anonymous',
        'login-anonymous',
        'signup-anonymous',
        'edit-author',
        'delete-author',
        'edit-reader',
        'delete-reader',
    ]
)
def test_pages_availability(
    url_name, user_role, expected_status,
    client, author_client, reader_client, request
):
    """Тестирует доступность страниц для разных пользователей."""
    url = request.getfixturevalue(url_name)

    if user_role == 'author':
        client_instance = author_client
    elif user_role == 'reader':
        client_instance = reader_client
    else:
        client_instance = client

    response = client_instance.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_name',
    ['comment_edit_url', 'comment_delete_url'],
    ids=['edit-redirect', 'delete-redirect']
)
def test_anonymous_redirects(client, url_name, login_url, request):
    """Тестирует редиректы для анонимного пользователя."""
    url = request.getfixturevalue(url_name)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url, follow=False)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url


def test_logout_page(client, logout_url):
    """Тестирует доступность страницы выхода."""
    response = client.post(logout_url)
    assert response.status_code == HTTPStatus.OK
