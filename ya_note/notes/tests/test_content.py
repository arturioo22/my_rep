from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNoteList(TestCase):
    """Тестирование списка заметок."""
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        """Создаём тестовые данные: двух пользователей и три заметки."""
        cls.author = User.objects.create(username='Автор заметок')
        cls.reader = User.objects.create(username='Другой пользователь')
        cls.note1 = Note.objects.create(
            title='Заметка 1',
            text='Текст заметки 1',
            author=cls.author,
            slug='note-1'
        )
        cls.note2 = Note.objects.create(
            title='Заметка 2',
            text='Текст заметки 2',
            author=cls.author,
            slug='note-2'
        )
        cls.foreign_note = Note.objects.create(
            title='Чужая заметка',
            text='Текст чужой заметки',
            author=cls.reader,
            slug='foreign-note'
        )

    def test_author(self):
        """Проверяем, что автор видит только свои заметки."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note1, object_list)
        self.assertIn(self.note2, object_list)
        self.assertNotIn(self.foreign_note, object_list)

    def test_note(self):
        """Проверяем, что отдельная заметка передаётся в object_list."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note1, object_list)


class TestNoteForms(TestCase):
    """Тестирование форм для заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создаём пользователя и заметку для тестов форм."""
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            author=cls.author,
            slug='test-note'
        )
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_create(self):
        """Проверяем, что страница создания заметки содержит форму."""
        self.client.force_login(self.author)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit(self):
        """Проверяем, что страница редактирования заметки содержит форму."""
        self.client.force_login(self.author)
        response = self.client.get(self.edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
