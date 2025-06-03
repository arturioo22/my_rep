from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Общие тестовые данные."""
        cls.author = User.objects.create(username='Автор заметок')
        cls.reader = User.objects.create(username='Другой пользователь')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')


class TestNoteList(BaseTestCase):
    """Тестирование списка заметок."""

    @classmethod
    def setUpTestData(cls):
        """Тестовые данные для заметок."""
        super().setUpTestData()
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
        cls.foreign_note = Note.objects.create(
            title='Чужая заметка',
            text='Текст чужой заметки',
            author=cls.reader,
            slug='foreign-note'
        )

    def test_author(self):
        """Проверяем, что автор видит только свои заметки."""
        response = self.author_client.get(self.list_url)
        notes = response.context['object_list']
        self.assertIn(self.first_note, notes)
        self.assertIn(self.second_note, notes)
        self.assertNotIn(self.foreign_note, notes)

    def test_note(self):
        """Проверяем, что отдельная заметка передаётся в список."""
        response = self.author_client.get(self.list_url)
        notes = response.context['object_list']
        self.assertIn(self.first_note, notes)


class TestNoteForms(BaseTestCase):
    """Тестирование форм для заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создаём пользователя и заметку для тестов форм."""
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            author=cls.author,
            slug='test-note'
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_create(self):
        """Проверяем, что страницы создания и редактирования содержат форму."""
        urls = (
            ('add_url', self.add_url),
            ('edit_url', self.edit_url),
        )
        for name, url in urls:
            with self.subTest(name=name):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context['form'],
                    NoteForm
                )
