from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class BceidUser(models.Model):
    """
    BCeID user table
    """

    user_guid = models.CharField(db_index=True, max_length=32, unique=True, blank=False)
    """ BCEID identifier for user """

    display_name = models.TextField(blank=True)
    """ BCEID display name """

    sm_user = models.TextField(blank=True)
    """ SiteMinder user value """

    date_joined = models.DateTimeField(default=timezone.now)
    """ First login timestamp """

    last_login = models.DateTimeField(default=timezone.now)
    """ Most recent login timestamp """

    has_seen_orders_page = models.BooleanField(default=False)
    """ Flag for intercept page """

    has_accepted_terms = models.BooleanField(default=False)
    """ Flag for accepting terms of service """

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    is_staff = True

    is_active = True

    def has_module_perms(self, *args):
        return True

    def has_perm(self, *args):
        return True

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
    """ For conditional questions, this is the question it is conditional upon """

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

    bceid_user = models.ForeignKey(BceidUser, related_name='responses', on_delete=models.CASCADE)
    """ User providing response """

    question = models.ForeignKey(Question, related_name='responses', on_delete=models.CASCADE)
    """ Originating question """

    value = models.TextField(blank=True)
    """ The question's response from the user """

    class Meta:
        unique_together = ("bceid_user", "question")

    def __str__(self):
        return '%s -> %s' % (self.bceid_user, self.question.key)


class DontLog:
    def log_addition(self, *args):
        return

    def log_change(self, *args):
        return

    def log_deletion(self, *args):
        return


class UserResponseAdmin(DontLog, admin.ModelAdmin):
    list_display = ['get_user_name', 'question', 'value']

    def get_user_name(self, obj):
        return obj.bceid_user.display_name

    get_user_name.admin_order_field = 'bceid_user'
    get_user_name.short_description = 'User'


class QuestionAdmin(DontLog, admin.ModelAdmin):
    pass


admin.site.register(BceidUser)
admin.site.register(Question, QuestionAdmin)
admin.site.register(UserResponse, UserResponseAdmin)
