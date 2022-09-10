"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""
from nqgcs import NQGCS

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from .settings import APP_FOLDER
from .gcs_url import gcs_url

url_signer = URLSigner(session)

BUCKET = '/Lexical_Libary'


GCS_KEY_PATH = os.path.join(
    APP_FOLDER, 'private/lexicallibary-a7fc05f5fa13.json')
with open(GCS_KEY_PATH) as gcs_key_f:
    GCS_KEYS = json.load(gcs_key_f)

# I create a handle to gcs, to perform the various operations.
gcs = NQGCS(json_key_path=GCS_KEY_PATH)

@action('index')
@action.uses('index.html', db, auth)
def index():
    print("User:", get_user_email())
    return dict()

@action('user_dictionaries')
@action.uses('user_dictionaries.html', url_signer, db, auth.user)
def index():
    return dict(
        # This is the signed URL for the callback.
        load_personal_dictionaries_url = URL('load_personal_dictionaries', signer=url_signer),
        load_username_url = URL('load_username', signer=url_signer),
        load_email_url = URL('load_email', signer=url_signer),
        add_dictionary_url = URL('add_dictionary', signer=url_signer),
        delete_dictionary_url = URL('delete_dictionary', signer=url_signer),
    )

@action('dictionary/<dictionary_id>')
@action.uses('dictionary.html', db, auth, url_signer)
def artwork(dictionary_id):
    return dict(
        # COMPLETE: return here any signed URLs you need.
        #my_callback_url = URL('my_callback', signer=url_signer),
        load_personal_dictionaries_url = URL('load_personal_dictionaries', signer=url_signer),
        load_dictionaries_url = URL('load_dictionaries', signer=url_signer),
        dictionary_id = dictionary_id,
        load_words_url=URL('load_words', signer=url_signer),
        load_username_url = URL('load_username', signer=url_signer),
        load_email_url = URL('load_email', signer=url_signer),
        add_word_url = URL('add_word', signer=url_signer),
        delete_word_url = URL('delete_word', signer=url_signer),
        edit_dictionary_url = URL('edit_dictionary', signer=url_signer),
    )



@action('load_personal_dictionaries')
@action.uses(url_signer.verify(), db)
def load_personal_dictionaries():
    rows = db(db.dictionary.created_by == get_user_email()).select().as_list()
    return dict(rows=rows)

@action('load_dictionaries')
@action.uses(url_signer.verify(), db)
def load_dictionaries():
    rows = db(db.dictionary).select().as_list()
    return dict(rows=rows)


@action('load_words')
@action.uses(url_signer.verify(), db)
def load_personal_dictionaries():
    rows = db(db.words).select().as_list()
    return dict(rows=rows)

@action('load_email')
@action.uses(url_signer.verify(), db)
def load_email():
    email = auth.current_user.get('email')
    return dict(email=email)

@action('load_username')
@action.uses(url_signer.verify(), db)
def load_name():
    username = auth.current_user.get('username')
    return dict(username=username)


@action('add_dictionary', method="POST")
@action.uses(url_signer.verify(), db, auth.user)
def add_dictionary():
    id = db.dictionary.insert(
        title=request.json.get('adding_title'),
        text=request.json.get('adding_text'),
        public=request.json.get('adding_public'),
    )
    return dict(id=id)

@action('add_word', method="POST")
@action.uses(url_signer.verify(), db, auth.user)
def add_word():
    id = db.words.insert(
        word=request.json.get('adding_word'),
        english=request.json.get('adding_english'),
        position=request.json.get('adding_position'),
        definition=request.json.get('adding_definition'),
        other=request.json.get('adding_other'),
        dictionary=request.json.get('adding_dictionary_id'),
    )
    return dict(id=id)

@action('edit_dictionary', method='POST')
@action.uses(url_signer.verify(), db, auth.user)
def edit_dictionary():
    print("piss")
    id = db.dictionary.update_or_insert(
        db.dictionary.id == request.json.get('edit_id'),
        title=request.json.get('edit_title'),
        text=request.json.get('edit_text'),
        public=request.json.get('edit_public'),
    )
    return dict(id=id)

@action('delete_dictionary')
@action.uses(url_signer.verify(), db, auth.user)
def delete_contact():
    id = request.params.get('id')
    assert id is not None
    db(db.dictionary.id == id).delete()
    return "ok"

@action('delete_word')
@action.uses(url_signer.verify(), db, auth.user)
def delete_word():
    id = request.params.get('id')
    assert id is not None
    db(db.words.id == id).delete()
    return "ok"

