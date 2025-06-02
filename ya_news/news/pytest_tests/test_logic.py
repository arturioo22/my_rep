from http import HTTPStatus

import pytest
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING

pytestmark = pytest.mark.django_db


def test_anonymous_comment(client, news):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.post(url, data={'text': 'Текст комментария'})
    login_url = reverse('users:login')
    redirect_url = f'{login_url}?next={url}'
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url
    assert news.comment_set.count() == 0


def test_authorized_comment(author_client, author, news):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=(news.pk,))
    comment_text = 'Текст комментария'
    response = author_client.post(url, data={'text': comment_text})
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{url}#comments'
    assert news.comment_set.count() == 1
    comment = news.comment_set.first()
    assert comment.text == comment_text
    assert comment.author == author
    assert comment.news == news


def test_bad_words(author_client, news):
    """Если комментарий содержит запрещённые слова, он не будет опубликован."""
    url = reverse('news:detail', args=(news.pk,))
    bad_text = f'Текст с запрещенным словом {BAD_WORDS[0]}'
    response = author_client.post(url, data={'text': bad_text})
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assert WARNING in response.context['form'].errors['text']
    assert news.comment_set.count() == 0


def test_author_comment(author_client, comment, news):
    """Авторизованный пользователь может редактировать свои комментарии."""
    edit_url = reverse('news:edit', args=(comment.pk,))
    new_text = 'Обновленный текст комментария'
    response = author_client.post(edit_url, data={'text': new_text})
    assert response.status_code == HTTPStatus.FOUND
    detail_url = reverse('news:detail', args=(news.pk,))
    expected_redirect_url = f"{detail_url}#comments"
    assert response.url == expected_redirect_url
    comment.refresh_from_db()
    assert comment.text == new_text


def test_author_delete_comment(author_client, comment, news):
    """Авторизованный пользователь может удалять свои комментарии."""
    delete_url = reverse('news:delete', args=(comment.pk,))
    response = author_client.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    news_detail_url = reverse('news:detail', args=(news.pk,))
    expected_redirect_url = f"{news_detail_url}#comments"
    assert response.url == expected_redirect_url
    assert news.comment_set.count() == 0


def test_edit_comment_another_user(reader_client, comment):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    edit_url = reverse('news:edit', args=(comment.pk,))
    response = reader_client.post(edit_url, data={'text': 'Новый текст'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    original_text = comment.text
    comment.refresh_from_db()
    assert comment.text == original_text


def test_delete_comment_another_user(reader_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    delete_url = reverse('news:delete', args=(comment.pk,))
    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.news.comment_set.count() == 1
