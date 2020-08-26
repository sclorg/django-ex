import clamd
from clamd import BufferTooLongError
from unittest import mock

from django import forms
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from ..validators import file_scan_validation


class TestUploadForm(forms.Form):
    upload = forms.FileField(validators=[file_scan_validation])


class UploadScanTests(TestCase):

    def test_validation_disabled(self):
        with self.settings(CLAMAV_ENABLED=False):
            infected = SimpleUploadedFile('infected.txt', clamd.EICAR)
            form = TestUploadForm(files={'upload': infected})

            self.assertTrue(form.is_valid(), form.errors)

    def test_validation_invalid_network_connection(self):
        with self.settings(CLAMAV_TCP_PORT=9999):
            infected = SimpleUploadedFile('infected.txt', clamd.EICAR)
            form = TestUploadForm(files={'upload': infected})

            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors['upload'][0], 'Unable to scan file.')

    @mock.patch('clamd.ClamdNetworkSocket.instream')
    def test_validation_buffer_overflow(self, mock_clam):
        mock_clam.side_effect = BufferTooLongError()

        # by default clamav has a 10mb limit for instream
        clean = SimpleUploadedFile('clean.txt', b'clean file')
        form = TestUploadForm(files={'upload': clean})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['upload'][0], 'Unable to scan file.')

    @mock.patch('clamd.ClamdNetworkSocket.instream')
    def test_validation_virus_found(self, mock_clam):
        mock_clam.return_value = {'stream': ('FOUND', 'Eicar-Test-Signature')}

        infected = SimpleUploadedFile('infected.txt', clamd.EICAR)
        form = TestUploadForm(files={'upload': infected})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['upload'][0], 'Infected file found.')

    @mock.patch('clamd.ClamdNetworkSocket.instream')
    def test_validation_no_virus_found(self, mock_clam):
        mock_clam.return_value = {'stream': ('OK', None)}

        clean = SimpleUploadedFile('clean.txt', b'clean file')
        form = TestUploadForm(files={'upload': clean})

        self.assertTrue(form.is_valid())
