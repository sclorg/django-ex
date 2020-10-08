import logging
import clamd
import sys

from rest_framework.exceptions import ValidationError
from django.conf import settings

logger = logging.getLogger(__name__)


def file_scan_validation(file):
    """
    This validator sends the file to ClamAV for scanning and returns returns to the form. By default, if antivirus
    service is not available or there are errors, the validation will fail.

    Usage:
        class UploadForm(forms.Form):
            file = forms.FileField(validators=[file_scan_validation])
    :param file:
    :return:
    """
    logger.debug("starting file scanning with clamav")
    if not settings.CLAMAV_ENABLED:
        logger.warning('File scanning has been disabled.')
        return

    # make sure we're at the beginning of the file stream
    file.seek(0)

    # we're just going to assume a network connection to clamav here .. no local unix socket support
    scanner = clamd.ClamdNetworkSocket(settings.CLAMAV_TCP_ADDR, settings.CLAMAV_TCP_PORT)
    try:
        result = scanner.instream(file)
    except:
        # it doesn't really matter what the actual error is .. log it and raise validation error
        logger.error('Error occurred while trying to scan file. "{}"'.format(sys.exc_info()[0]))
        raise ValidationError('Unable to scan file.', code='scanerror')
    finally:
        # reset file stream
        file.seek(0)

    if result and result['stream'][0] == 'FOUND':
        logger.warning('Virus found: {}'.format(file.name))
        raise ValidationError('Infected file found.', code='infected')


def valid_file_extension(file):
    extension = file.name.split('.')[-1]
    if extension.lower() not in ['pdf', 'png', 'gif', 'jpg', 'jpe', 'jpeg']:
        raise ValidationError(f'File type not supported: {extension}')


def valid_doc_type(value):
    valid_codes = ['AAI', 'AFDO', 'AFTL', 'CSA', 'EFSS', 'MC', 'NCV', 'OFI', 'RDP']
    if value.upper() not in valid_codes:
        raise ValidationError(f'Doc type not supported: {value}. Valid codes: {", ".join(valid_codes)}')


def valid_rotation(value):
    if value % 90 != 0:
        raise ValidationError('Rotation must be 0, 90, 180, or 270')
