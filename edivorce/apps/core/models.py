from django.contrib.auth.models import User
from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class BceidUser(models.Model):
    """
    BCeID user table
    """

    user_guid = models.CharField(db_index=True, max_length=36, unique=True, blank=False)
    """ BCEID identifier for user """

    date_joined = models.DateTimeField(default=timezone.now)
    """ First login timestamp """

    last_login = models.DateTimeField(default=timezone.now)
    """ Most recent login timestamp """

    def __str__(self):
        return 'BCeID User %s' % self.user_guid



@python_2_unicode_compatible
class Question(models.Model):
    """
    Questions being asked of the user, later assembled into LegalForms.

    NOTE: The content and interaction of the question is defined in the
    template; the name and description field here are for admin use.
    """

    key = models.TextField(primary_key=True)
    """ Unique question identifier """

    name = models.TextField(blank=True)
    """ Readable name of question (n.b., NOT content) """

    description = models.TextField(blank=True)
    """ Extended description (n.b., NOT content) """

    class Meta:
        ordering = ('key', )

    def __str__(self):
        return '%s: %s' % (self.key, self.name)


@python_2_unicode_compatible
class LegalForm(models.Model):
    """
    A defined legal filing composed of a template and mapped response values
    """

    key = models.TextField(primary_key=True)
    """ Form ID (e.g., 'f1') """

    name = models.TextField()
    """ Full name of form (e.g., 'Notice of Joint Family Claim') """

    questions = models.ManyToManyField(Question, through='FormQuestions')
    """ Responses needed to complete the form, mapped through the question """

    order = models.PositiveIntegerField(default=0)
    """ Convenience for listing these in the admin """

    class Meta:
        verbose_name_plural = 'Legal Forms'
        ordering = ('order', )

    def __str__(self):
        return '%s: %s' % (str(self.key).upper(), self.name)


@python_2_unicode_compatible
class FormQuestions(models.Model):
    """
    Through class mapping questions to forms using their responses.

    This is an explicitly defined through model mainly to provide an opening
    for a transformational step on rendering per form.  The presence of a
    mapping here is for including the user's data during template rendering,
    not to logically connect/require the question be present or used.
    """

    legal_form = models.ForeignKey(LegalForm)
    """ The LegalForm """

    question = models.ForeignKey(Question)
    """ The Question """

    transformation = models.TextField()
    """ Transformations done on the value as part of rendering it in a form """
    # placeholder for code or flags need to modified to fit into a form

    class Meta:
        verbose_name_plural = 'Form Questions'

    def __str__(self):
        return '%s -> %s' % (self.legal_form.key.upper(), self.question.key)


@python_2_unicode_compatible
class UserResponse(models.Model):
    """
    User input
    """

    bceid_user = models.ForeignKey(BceidUser)
    """ User providing response """

    question = models.ForeignKey(Question)
    """ Originating question """

    value = models.TextField(blank=True)
    """ The question's response from the user """

    def __str__(self):
        return '%s -> %s' % (self.bceid_user, self.question.key)


admin.site.register(BceidUser)
admin.site.register(Question)
admin.site.register(LegalForm)
admin.site.register(UserResponse)
admin.site.register(FormQuestions)
