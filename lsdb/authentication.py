from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from datetime import timedelta
from django.utils import timezone
from django.conf import settings
# from .email import * # feels somwhat wrong to be emailing here
# from .utils import encrypt


#this return left time
def expires_in(token):
    time_elapsed = timezone.now() - token.created
    left_time = timedelta(seconds = settings.TOKEN_EXPIRED_AFTER_SECONDS) - time_elapsed
    return left_time

# token checker if token expired or not
def is_token_expired(token):
    return expires_in(token) < timedelta(seconds = 0)

# if token is expired new token will be established
# If token is expired then it will be removed
# and new one with different key will be created
def token_expire_handler(token):
    is_expired = is_token_expired(token)
    if is_expired:
        # send email with magic_link: (TODO: Decide on this)
        # note = Notification()
        # note.throttled_email(template='confirm_account',
        #     username = token.user.username,
        #     magic_link =  settings.CLIENT_HOST + '/login/' + encrypt(token))

        # TODO: this used to refresh the token in lieu of some other behavior
        token = token_refresh(token)
        is_expired = False
    return is_expired, token

def token_refresh(token):
    token.delete()
    token = Token.objects.create(user = token.user)
    return token

#________________________________________________
#DEFAULT_AUTHENTICATION_CLASSES
class ExpiringTokenAuthentication(TokenAuthentication):
    """
    If token is expired then it will be removed
    and new one with different key will be created
    """
    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key = key)
        except Token.DoesNotExist:
            raise AuthenticationFailed("Invalid Token")

        if not token.user.is_active:
            raise AuthenticationFailed("User is not active")

        is_expired, token = token_expire_handler(token)
        if is_expired:
            # deactivate user
            raise AuthenticationFailed("User session expired or unrecognized device login. Please verify your identity using the link that has been emailed to {0}.".format(token.user.email))
            # TODO: Send `re-activate your account` email

        # If we don't error out then we refresh the token:
        # token = token_refresh(token)
        return (token.user, token)
