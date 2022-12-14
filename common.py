"""
This file defines cache, session, and translator T object for the app
These are fixtures that every app needs so probably you will not be editing this file
"""
import copy
import os
import sys
import logging
from pydal.validators import (CRYPT, IS_EMAIL, IS_EQUAL_TO, IS_MATCH,
                              IS_NOT_EMPTY, IS_NOT_IN_DB, IS_STRONG)
from py4web import Session, Cache, Translator, Flash, DAL, Field, action
from py4web.utils.mailer import Mailer
from py4web.utils.auth import Auth
from py4web.utils.downloader import downloader
from pydal.tools.tags import Tags
from py4web.utils.factories import ActionFactory
from py4web.utils.form import FormStyleBulma
from . import settings

class MyAuth(Auth):
    
    MESSAGES = {
        "verify_email": {
            "subject": "Confirm email",
            "body": "Welcome {username}, click {link} to confirm your email",
        },
        "reset_password": {
            "subject": "Password reset",
            "body": "Hello {username}, click {link} to change password",
        },
        "unsubscribe": {
            "subject": "Unsubscribe confirmation",
            "body": "By {username}, you have been erased from our system",
        },
        "flash": {
            "user-registered": "User registered",
            "password-reset-link-sent": "Password reset link sent",
            "password-changed": "Password changed",
            "profile-saved": "Profile saved",
            "user-logout": "User logout",
            "email-verified": "Email verified",
            "link-expired": "Link invalid or expired",
        },
        "labels": {
            "username": "Username",
            "email": "Email",
            "first_name": "First Name",
            "last_name": "Last Name",
            "phone_number": "Phone Number",
            "username_or_email": "Username or Email",
            "password": "Password",
            "new_password": "New Password",
            "old_password": "Old Password",
            "login_password": "Password",
            "password_again": "Password (again)",
            "created_on": "Created On",
            "created_by": "Created By",
            "modified on": "Modified On",
            "modified by": "Modified By",
        },
        "buttons": {
            "lost-password": "Lost Password",
            "register": "Register",
            "request": "Request",
            "sign-in": "Sign In",
            "sign-up": "Sign Up",
            "submit": "Submit",
        },
        "errors": {
            "invalid_username": "Invalid username",
            "invalid_email": "Invalid email",
            "registration_is_pending": "Registration is pending",
            "account_is_blocked": "Account is blocked",
            "account_needs_to_be_approved": "Account needs to be approved",
            "invalid_credentials": "Invalid Credentials",
            "invalid_token": "invalid token",
            "password_doesnt_match": "Password doesn't match",
            "invalid_current_password": "invalid current password",
            "new_password_is_the_same_as_previous_password": "new password is the same as previous password",
            "new_password_was_already_used": "new password was already used",
            "invalid": "invalid",
            "no_json_post_payload": "no json post payload",
        },
    }

    def define_tables(self):
        """Defines the auth_user table"""
        db = self.db
        if "auth_user" not in db.tables:
            ne = IS_NOT_EMPTY()
            if self.param.password_complexity:
                requires = [IS_STRONG(**self.param.password_complexity), CRYPT()]
            else:
                requires = [CRYPT()]
            auth_fields = [
                Field(
                    "email",
                    requires=(IS_EMAIL(), IS_NOT_IN_DB(db, "auth_user.email")),
                    unique=True,
                    label=self.param.messages["labels"].get("email"),
                ),
                Field(
                    "password",
                    "password",
                    requires=requires,
                    readable=False,
                    writable=False,
                    label=self.param.messages["labels"].get("password"),
                ),
                Field("sso_id", readable=False, writable=False),
                Field("action_token", readable=False, writable=False),
                Field(
                    "last_password_change",
                    "datetime",
                    default=None,
                    readable=False,
                    writable=False,
                ),
            ]
            if self.use_username:
                auth_fields.insert(
                    0,
                    Field(
                        "username",
                        requires=[ne, IS_NOT_IN_DB(db, "auth_user.username")],
                        unique=True,
                        label=self.param.messages["labels"].get("username"),
                    ),
                )
            if self.use_phone_number:
                auth_fields.insert(
                    2,
                    Field(
                        "phone_number",
                        requires=[
                            ne,
                            IS_MATCH(r"^[+]?(\(\d+\)|\d+)(\(\d+\)|\d+|[ -])+$"),
                        ],
                        label=self.param.messages["labels"].get("phone_number"),
                    ),
                )
            if self.param.block_previous_password_num is not None:
                auth_fields.append(
                    Field(
                        "past_passwords_hash",
                        "list:string",
                        writable=False,
                        readable=False,
                    )
                )
            db.define_table("auth_user", *(auth_fields + self.extra_auth_user_fields))




# #######################################################
# implement custom loggers form settings.LOGGERS
# #######################################################
logger = logging.getLogger("py4web:" + settings.APP_NAME)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)
for item in settings.LOGGERS:
    level, filename = item.split(":", 1)
    if filename in ("stdout", "stderr"):
        handler = logging.StreamHandler(getattr(sys, filename))
    else:
        handler = logging.FileHandler(filename)
    handler.setFormatter(formatter)
    logger.setLevel(getattr(logging, level.upper(), "DEBUG"))
    logger.addHandler(handler)

# #######################################################
# connect to db
# #######################################################
if os.environ.get("GAE_ENV"):
    db = DAL(
        settings.CLOUD_DB_URI,
        folder=settings.CLOUD_DB_FOLDER,
        pool_size=settings.CLOUD_DB_POOL_SIZE,
        migrate=settings.CLOUD_DB_MIGRATE,
        fake_migrate=settings.CLOUD_DB_FAKE_MIGRATE,
    )
else:
    db = DAL(
        settings.DB_URI,
        folder=settings.DB_FOLDER,
        pool_size=settings.DB_POOL_SIZE,
        migrate=settings.DB_MIGRATE,
        fake_migrate=settings.DB_FAKE_MIGRATE,
    )

# #######################################################
# define global objects that may or may not be used by the actions
# #######################################################
cache = Cache(size=1000)
T = Translator(settings.T_FOLDER)
flash = Flash()

# #######################################################
# pick the session type that suits you best
# #######################################################
if settings.SESSION_TYPE == "cookies":
    session = Session(secret=settings.SESSION_SECRET_KEY)
elif settings.SESSION_TYPE == "redis":
    import redis

    host, port = settings.REDIS_SERVER.split(":")
    # for more options: https://github.com/andymccurdy/redis-py/blob/master/redis/client.py
    conn = redis.Redis(host=host, port=int(port))
    conn.set = (
        lambda k, v, e, cs=conn.set, ct=conn.ttl: cs(k, v, ct(k))
        if ct(k) >= 0
        else cs(k, v, e)
    )
    session = Session(secret=settings.SESSION_SECRET_KEY, storage=conn)
elif settings.SESSION_TYPE == "memcache":
    import memcache, time

    conn = memcache.Client(settings.MEMCACHE_CLIENTS, debug=0)
    session = Session(secret=settings.SESSION_SECRET_KEY, storage=conn)
elif settings.SESSION_TYPE == "database":
    from py4web.utils.dbstore import DBStore

    session = Session(secret=settings.SESSION_SECRET_KEY, storage=DBStore(db))

# #######################################################
# Instantiate the object and actions that handle auth
# #######################################################

auth = MyAuth(session, db, define_tables=False)

# Fixes the messages.
auth_messages = copy.deepcopy(auth.MESSAGES)
auth_messages['buttons']['sign-in'] = "Log in"
auth_messages['buttons']['sign-up'] = "Sign up"
auth_messages['buttons']['lost-password'] = "Lost password"

# And button classes.
auth_button_classes = {
    "lost-password": "button is-danger is-light",
    "register": "button is-info is-light",
    "request": "button is-primary",
    "sign-in": "button is-primary",
    "sign-up": "button is-success",
    "submit": "button is-primary",
}

auth.use_username = True
auth.param.button_classes = auth_button_classes
auth.param.registration_requires_confirmation = False
auth.param.registration_requires_approval = False
auth.param.allowed_actions = settings.ALLOWED_ACTIONS
auth.param.login_expiration_time = 3600
# FIXME: Readd for production.
auth.param.password_complexity = {"entropy": 2}
auth.param.block_previous_password_num = 3
auth.param.formstyle = FormStyleBulma
auth.define_tables()

# #######################################################
# Configure email sender for auth
# #######################################################
if settings.SMTP_SERVER:
    auth.sender = Mailer(
        server=settings.SMTP_SERVER,
        sender=settings.SMTP_SENDER,
        login=settings.SMTP_LOGIN,
        tls=settings.SMTP_TLS,
        ssl=settings.SMTP_SSL,
    )

# #######################################################
# Create a table to tag users as group members
# #######################################################
if auth.db:
    groups = Tags(db.auth_user, "groups")

# #######################################################
# Enable optional auth plugin
# #######################################################
if settings.USE_PAM:
    from py4web.utils.auth_plugins.pam_plugin import PamPlugin

    auth.register_plugin(PamPlugin())

if settings.USE_LDAP:
    from py4web.utils.auth_plugins.ldap_plugin import LDAPPlugin

    auth.register_plugin(LDAPPlugin(db=db, groups=groups, **settings.LDAP_SETTINGS))

if settings.OAUTH2GOOGLE_CLIENT_ID:
    from py4web.utils.auth_plugins.oauth2google import OAuth2Google  # TESTED

    auth.register_plugin(
        OAuth2Google(
            client_id=settings.OAUTH2GOOGLE_CLIENT_ID,
            client_secret=settings.OAUTH2GOOGLE_CLIENT_SECRET,
            callback_url="auth/plugin/oauth2google/callback",
        )
    )
if settings.OAUTH2FACEBOOK_CLIENT_ID:
    from py4web.utils.auth_plugins.oauth2facebook import OAuth2Facebook  # UNTESTED

    auth.register_plugin(
        OAuth2Facebook(
            client_id=settings.OAUTH2FACEBOOK_CLIENT_ID,
            client_secret=settings.OAUTH2FACEBOOK_CLIENT_SECRET,
            callback_url="auth/plugin/oauth2facebook/callback",
        )
    )

if settings.OAUTH2OKTA_CLIENT_ID:
    from py4web.utils.auth_plugins.oauth2okta import OAuth2Okta  # TESTED

    auth.register_plugin(
        OAuth2Okta(
            client_id=settings.OAUTH2OKTA_CLIENT_ID,
            client_secret=settings.OAUTH2OKTA_CLIENT_SECRET,
            callback_url="auth/plugin/oauth2okta/callback",
        )
    )

# #######################################################
# Define a convenience action to allow users to download
# files uploaded and reference by Field(type='upload')
# #######################################################
#if settings.UPLOAD_FOLDER:
#    @action('download/<filename>')
#    @action.uses(db)
#    def download(filename):
#        return downloader(db, settings.UPLOAD_FOLDER, filename)
    # To take advantage of this in Form(s)
    # for every field of type upload you MUST specify:
    #
    # field.upload_path = settings.UPLOAD_FOLDER
    # field.download_url = lambda filename: URL('download/%s' % filename)

# #######################################################
# Optionally configure celery
# #######################################################
if settings.USE_CELERY:
    from celery import Celery

    # to use "from .common import scheduler" and then use it according
    # to celery docs, examples in tasks.py
    scheduler = Celery(
        "apps.%s.tasks" % settings.APP_NAME, broker=settings.CELERY_BROKER
    )


# #######################################################
# Enable authentication
# #######################################################
auth.enable(uses=(session, T, db), env=dict(T=T))

# #######################################################
# Define convenience decorators
# #######################################################
unauthenticated = ActionFactory(db, session, T, flash, auth)
authenticated = ActionFactory(db, session, T, flash, auth.user)