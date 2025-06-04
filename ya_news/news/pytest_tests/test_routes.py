import pytest

from http import HTTPStatus

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_name, client_fixture, expected_status',
    [
        ('home_url', 'client', HTTPStatus.OK),
        ('detail_url', 'client', HTTPStatus.OK),
        ('login_url', 'client', HTTPStatus.OK),
        ('signup_url', 'client', HTTPStatus.OK),
        ('comment_edit_url', 'author_client', HTTPStatus.OK),
        ('comment_delete_url', 'author_client', HTTPStatus.OK),
        ('comment_edit_url', 'reader_client', HTTPStatus.NOT_FOUND),
        ('comment_delete_url', 'reader_client', HTTPStatus.NOT_FOUND),
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
    url_name, client_fixture, expected_status, request
):
    """Тестирует доступность страниц для разных пользователей."""
    url = request.getfixturevalue(url_name)
    client = request.getfixturevalue(client_fixture)
    response = client.get(url)
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
