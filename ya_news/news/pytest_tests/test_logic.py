from http import HTTPStatus

import pytest
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_comment(client, news, detail_url, login_url):
    """Анонимный пользователь не может отправить комментарий."""
    initial_count = news.comment_set.count()
    response = client.post(detail_url, data={'text': 'Текст комментария'})
    redirect_url = f'{login_url}?next={detail_url}'
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url
    assert news.comment_set.count() == initial_count


def test_authorized_comment(author_client, author, news, detail_url):
    """Авторизованный пользователь может отправить комментарий."""
    Comment.objects.all().delete()
    initial_count = news.comment_set.count()
    comment_text = 'Текст комментария'
    response = author_client.post(detail_url, data={'text': comment_text})
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{detail_url}#comments'
    assert news.comment_set.count() == initial_count + 1
    comment = news.comment_set.get()
    assert comment.text == comment_text
    assert comment.author == author
    assert comment.news == news


def test_bad_words(author_client, news, detail_url):
    """Если комментарий содержит запрещённые слова, он не будет опубликован."""
    initial_count = news.comment_set.count()
    bad_text = f'Текст с запрещенным словом {BAD_WORDS[0]}'
    response = author_client.post(detail_url, data={'text': bad_text})
    assert response.status_code == HTTPStatus.OK
    assert news.comment_set.count() == initial_count
    assert 'form' in response.context
    assert WARNING in response.context['form'].errors['text']


def test_author_comment(author_client, comment, news, detail_url):
    """Авторизованный пользователь может редактировать свои комментарии."""
    initial_count = news.comment_set.count()
    edit_url = reverse('news:edit', args=(comment.pk,))
    new_text = 'Обновленный текст комментария'
    response = author_client.post(edit_url, data={'text': new_text})
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f"{detail_url}#comments"
    assert news.comment_set.count() == initial_count
    updated_comment = news.comment_set.get(pk=comment.pk)
    assert updated_comment.text == new_text
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_author_delete_comment(author_client, comment, news, detail_url):
    """Авторизованный пользователь может удалять свои комментарии."""
    initial_count = news.comment_set.count()
    delete_url = reverse('news:delete', args=(comment.pk,))
    response = author_client.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f"{detail_url}#comments"
    assert news.comment_set.count() == initial_count - 1


def test_edit_comment_another_user(reader_client, comment):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    original_data = {
        'text': comment.text,
        'author': comment.author,
        'news': comment.news,
        'created': comment.created
    }
    edit_url = reverse('news:edit', args=(comment.pk,))
    response = reader_client.post(edit_url, data={'text': 'Новый текст'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == original_data['text']
    assert updated_comment.author == original_data['author']
    assert updated_comment.news == original_data['news']
    assert updated_comment.created == original_data['created']


def test_delete_comment_another_user(reader_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    initial_count = comment.news.comment_set.count()
    delete_url = reverse('news:delete', args=(comment.pk,))
    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.news.comment_set.count() == initial_count
