from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class BceidUser(models.Model):
    """
    BCeID user table
    """

    user_guid = models.CharField(db_index=True, max_length=200, unique=True, blank=False)
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
    Questions being asked of the user.
    """

    key = models.TextField(primary_key=True)
    """ Unique question identifier """

    name = models.TextField(blank=True)
    """ Readable name of question (n.b., NOT content) """

    description = models.TextField(blank=True)
    """ Extended description (n.b., NOT content) """

    summary_order = models.PositiveIntegerField(default=0)
    """ Convenience for listing these in the admin """

    required = models.TextField(blank=True)
    """ 'Required', 'Conditional', or '' [blank = not required] """

    conditional_target = models.TextField(blank=True)
    """ For conditionally required questions, this is the other question that it is conditional upon """

    reveal_response = models.TextField(blank=True)
    """ The value of the other question that makes this question required """

    class Meta:
        ordering = ('summary_order', )

    def __str__(self):
        return '%s: %s' % (self.key, self.name)


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

    class Meta:
        unique_together = ("bceid_user", "question")

    def __str__(self):
        return '%s -> %s' % (self.bceid_user, self.question.key)


admin.site.register(BceidUser)
admin.site.register(Question)
admin.site.register(UserResponse)
