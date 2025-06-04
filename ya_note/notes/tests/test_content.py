from notes.forms import NoteForm
from .conftest import BaseTestCase


class TestNoteList(BaseTestCase):
    """Тестирование списка заметок."""

    def test_author_sees_only_own_notes(self):
        """Проверяем, что автор видит только свои заметки."""
        response = self.author_client.get(self.urls['list'])
        notes = response.context['object_list']
        self.assertIn(self.first_note, notes)
        self.assertIn(self.second_note, notes)
        self.assertNotIn(self.foreign_note, notes)

    def test_single_note_in_list(self):
        """Проверяем, что отдельная заметка передаётся в список."""
        response = self.author_client.get(self.urls['list'])
        notes = response.context['object_list']
        self.assertIn(self.note, notes)


class TestNoteForms(BaseTestCase):
    """Тестирование форм для заметок."""

    def test_create_and_edit_pages_contain_form(self):
        """Проверяем, что страницы создания и редактирования содержат форму."""
        test_cases = [
            ('add_page', self.urls['add']),
            ('edit_page', self.urls['edit'])
        ]

        for name, url in test_cases:
            with self.subTest(name=name):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
