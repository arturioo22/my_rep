from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    """Общие тестовые данные."""

    # Константы для тестовых данных
    NOTE_TITLE = 'Тестовая заметка'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'test-note'
    NEW_TITLE = 'Новый заголовок'
    NEW_TEXT = 'Новый текст'
    NEW_SLUG = 'new-slug'

    @classmethod
    def setUpTestData(cls):
        # Общие данные для всех тестов
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')

        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)

        # Тестовая заметка
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )

        # Заметки автора
        cls.first_note = Note.objects.create(
            title='Первая заметка',
            text='Текст первой заметки',
            author=cls.author,
            slug='first-note'
        )
        cls.second_note = Note.objects.create(
            title='Вторая заметка',
            text='Текст второй заметки',
            author=cls.author,
            slug='second-note'
        )

        # Чужая заметка
        cls.foreign_note = Note.objects.create(
            title='Чужая заметка',
            text='Текст чужой заметки',
            author=cls.reader,
            slug='foreign-note'
        )

        # URL-адреса
        cls.urls = {
            'add': reverse('notes:add'),
            'delete': reverse('notes:delete', args=(cls.note.slug,)),
            'detail': reverse('notes:detail', args=(cls.note.slug,)),
            'edit': reverse('notes:edit', args=(cls.note.slug,)),
            'home': reverse('notes:home'),
            'list': reverse('notes:list'),
            'login': reverse('users:login'),
            'signup': reverse('users:signup'),
            'success': reverse('notes:success')
        }

        # Данные для создания заметки
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

        # Данные для редактирования
        cls.edit_form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT,
            'slug': cls.NEW_SLUG
        }
