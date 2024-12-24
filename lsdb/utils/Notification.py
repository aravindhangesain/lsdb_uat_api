from datetime import timedelta
from threading import Thread
from typing import TypedDict, Any, List

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import django.template as DjangoTemplate
# from django.template import Context as DjangoContext
# from django.template.Engine import from_string
from django.utils import timezone

from lsdb.models import NotificationQueue
from lsdb.models import Template

class Notification(Thread):
    SUBJECTS = {
        'account_create': "Welcome to LSDB!",
        'confirm_account': "Verify your identity",
        'reset_password': "Reset your password",
        'assigned_owner': "LSDB ticket assigned to you",
        'overdue_ticket': 'LSDB ticket overdue',
        'requested_file': 'The file you requested is available.',
        'tagged_user': 'You have been tagged on an LSDB ticket.',
        'ticket_activity': 'New activity on an LSDB ticket.'
    }

    # Using the NotificationQueue as a log
    def __init__(self, **kwargs):
        Thread.__init__(self)

    def throttled_email(self, **kwargs):
        self.email_payload = kwargs
        self.start()

    def run(self):
        # Never want to send the same subject email to the same user
        # within 15 minutes(?) should be in settings.
        # print("Started sending email...")
        kwargs = self.email_payload

        user = kwargs.get('user')
        # subject = self.SUBJECTS.get(kwargs['template'])
        # print('Template:', kwargs['template'])
        template = Template.objects.get(name = kwargs['template'])
        body = template.body_source
        subject = template.subject_source # TODO Use factory
        resend_window = timezone.now() - timedelta(minutes=15)
        resend_window = timezone.now() - timedelta(seconds=10)

        if kwargs.get('resend'):
            subject = kwargs['original_msg'].subject
            user = kwargs['original_msg'].recipient
        elif kwargs.get('template') and kwargs.get('ticket_id', None):
            subject = '[#{}] - {}'.format(kwargs.get('ticket_id'), subject)
        # Check the queue for a duplicate message;
        try:
            duplicate = NotificationQueue.objects.get(
                queued_date__gte=resend_window,
                recipient=user,
                subject=subject
            )
        except NotificationQueue.DoesNotExist:
            # print('thinking about sending')
            if kwargs.get("group", None):
                self.email_group(subject=subject, body=body, **kwargs)
            else:
                self.email_user(subject=subject, body=body, **kwargs)

    # Currently not in use, remove this when you use it
    def email_entity(self, entity, template, items=None):
        # get all the users in the entity
        for user in userlist:
            self.email_user(username, template, items)
        pass

    def email_everyone(self):
        # Highly dangerous
        pass

    def email_group(self, **kwargs):
        group = kwargs["group"]

        for user in group.users.all():
            self.email_user(user=user, **kwargs)

    def email_followers(self, kwargs):
        pass

    # def email_user(self, username, template, items=None, magic_link=None):
    def email_user(self, **kwargs):
        # Really need to log errors so that we can identify invalid email addresses
        # as we try to send to them.
        # print("Sending email to user...")
        if kwargs.get('resend'):
            # do the needful
            note = kwargs.get('original_msg')
            subject = note.subject
            user = note.recipient
            text_content = note.text_body
            html_content = note.html_body
        else:
            user = kwargs['user']
            subject = kwargs['subject']
            plaintext = get_template('txt_error.txt')
            # html = get_template(kwargs['template'] + '.html')
            body = kwargs.pop('body')
            # print(body)
            html = DjangoTemplate.Engine.from_string(None, body)
            # msg_data = DjangoContext({"first_name": user.first_name, **kwargs})
            msg_data = {"first_name": user.first_name, **kwargs}
            # print(msg_data)
            # This parameter handling is a KLUGE that needs fixing
            # Sender needs to build full url for magic_links
            # msg_data['items'] = kwargs.get('items',None)
            # msg_data['MFR'] = kwargs.get('MFR',None)
            text_content = plaintext.render(msg_data)
            html_content = html.render(DjangoTemplate.Context(msg_data))
        # short circuit for disabled users:

        msg = EmailMultiAlternatives(subject,
                                     text_content, 'support@pvel.com', [user.username])
        msg.attach_alternative(html_content, "text/html")

        attachments = kwargs.get("attachments", None)
        if attachments:
            for attachment in attachments:
                msg.attach(attachment["file_name"], attachment["file_data"], attachment["mime_type"])

        if user.is_active:
            # Need to trap errors better here
            msg.send(fail_silently=False)

            sent_message = NotificationQueue.objects.create(
                transport='EMAIL',
                recipient=user,
                subject=subject,
                text_body=text_content,
                html_body=html_content,
                # queued_date is automatic
                sent=True  # KLUGE: Eror handling should allow for queuing
            )
        else:
            pass # don't actually send to disabled users

    def send(self):
        # still only doing email:
        self.email.send(fail_silently=False)
