from http import HTTPStatus

from django.contrib.auth import get_user
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .conftest import BaseTestCase


class TestNoteCreation(BaseTestCase):

    def test_user(self):
        """Залогиненный пользователь может создать заметку."""
        Note.objects.all().delete()
        initial_count = Note.objects.count()
        self.assertEqual(initial_count, 0)
        response = self.author_client.post(
            self.urls['add'], data=self.form_data
        )
        self.assertRedirects(response, self.urls['success'])
        self.assertEqual(Note.objects.count(), initial_count + 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, get_user(self.author_client))

    def test_anonymous(self):
        """Анонимный пользователь не может создать заметку."""
        initial_count = Note.objects.count()
        response = self.client.post(self.urls['add'], data=self.form_data)
        redirect_url = f"{self.urls['login']}?next={self.urls['add']}"
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_slug(self):
        """Если slug не указан, он формируется автоматически."""
        Note.objects.all().delete()
        self.assertEqual(Note.objects.count(), 0)
        self.form_data.pop('slug')
        response = self.author_client.post(
            self.urls['add'], data=self.form_data
        )
        self.assertRedirects(response, self.urls['success'])
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note.slug, expected_slug)

    def test_duplicate(self):
        """Невозможно создать две заметки с одинаковым slug."""
        initial_count = Note.objects.count()
        response = self.author_client.post(
            self.urls['add'],
            data=self.form_data,
            follow=True
        )
        self.assertEqual(Note.objects.count(), initial_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('slug', form.errors)
        self.assertEqual(
            form.errors['slug'],
            [self.NOTE_SLUG + WARNING]
        )


class TestNoteEditDelete(BaseTestCase):

    def test_author_edit(self):
        """Автор может редактировать свою заметку."""
        initial_count = Note.objects.count()
        response = self.author_client.post(
            self.urls['edit'], data=self.edit_form_data
        )
        self.assertRedirects(response, self.urls['success'])
        self.assertEqual(Note.objects.count(), initial_count)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.edit_form_data['title'])
        self.assertEqual(updated_note.text, self.edit_form_data['text'])
        self.assertEqual(updated_note.slug, self.edit_form_data['slug'])
        self.assertEqual(updated_note.author, self.note.author)

    def test_user_edit(self):
        """Пользователь не может редактировать чужую заметку."""
        initial_count = Note.objects.count()
        response = self.reader_client.post(
            self.urls['edit'], data=self.edit_form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(note_from_db.author, self.note.author)

    def test_author_delete(self):
        """Автор может удалить свою заметку."""
        initial_count = Note.objects.count()
        response = self.author_client.delete(self.urls['delete'])
        self.assertRedirects(response, self.urls['success'])
        self.assertEqual(Note.objects.count(), initial_count - 1)

    def test_user_delete(self):
        """Пользователь не может удалить чужую заметку."""
        initial_count = Note.objects.count()
        response = self.reader_client.delete(self.urls['delete'])
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
