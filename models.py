"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()

def get_user():
    return auth.current_user.get('id') if auth.current_user else None


db.define_table('dictionary',
                Field('title', length=100, requires=IS_NOT_EMPTY()),
                Field('text'),
                Field('created_by', default=get_user_email),
                Field('public', 'boolean', default='false'),
                )

db.define_table('words',
                Field('dictionary', 'reference dictionary'),
                Field('word', length=200, requires=IS_NOT_EMPTY()),
                Field('position', length=40),
                Field('english', length=100),
                Field('definition', requires=IS_NOT_EMPTY()),
                Field('other'),
                )

db.commit()

