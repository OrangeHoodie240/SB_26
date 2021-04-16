"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from psycopg2.errors import UniqueViolation
from app import app
import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    # Does the repr method work as expected?

    def test_repr(self):
        username = 'jotaro'
        email = 'jotaro@jojo.com'
        user = User(username=username, email=email, id=1001)
        user_id = user.id

        expected_repr = f'<User #{user_id}: {username}, {email}>'
        actual_repr = user.__repr__()
        self.assertEqual(actual_repr, expected_repr)

    # Does is_following successfully detect when user1 is following user2?

    def test_is_following_detect_following_user(self):
        user1 = User(username='name1', email='email1@email.com',
                     password='password1')
        user2 = User(username='name2', email='email2@email.com',
                     password='password2')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        follows = Follows(user_being_followed_id=user2.id,
                          user_following_id=user1.id)
        db.session.add(follows)
        db.session.commit()

        is_following = user1.is_following(user2)
        self.assertTrue(is_following)

    # Does is_following successfully detect when user1 is not following user2?
    def test_is_following_detect_not_following_user(self):
        user1 = User(username='name1', email='email1@email.com',
                     password='password1')
        user2 = User(username='name2', email='email2@email.com',
                     password='password2')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        is_following = user1.is_following(user2)
        self.assertFalse(is_following)

    # Does is_followed_by successfully detect when user1 is followed by user2?
    def test_is_followed_by_detect_following_user(self):
        user1 = User(username='name1', email='email1@email.com',
                     password='password1')
        user2 = User(username='name2', email='email2@email.com',
                     password='password2')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        follows = Follows(user_being_followed_id=user1.id,
                          user_following_id=user2.id)
        db.session.add(follows)
        db.session.commit()

        is_followed_by = user1.is_followed_by(user2)
        self.assertTrue(is_followed_by)

    # Does is_followed_by successfully detect when user1 is not followed by user2?

    def test_is_followed_by_detect_not_following_user(self):
        user1 = User(username='name1', email='email1@email.com',
                     password='password1')
        user2 = User(username='name2', email='email2@email.com',
                     password='password2')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        is_followed_by = user1.is_followed_by(user2)
        self.assertFalse(is_followed_by)

    # Does User.create successfully create a new user given valid credentials?
    def test_user_create_creates_new_user(self):
        user = User.signup('name1','email1@email.com', 'password1', '')
        db.session.commit()

        self.assertIsNotNone(user.id)

    # Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?
    def test_user_create_fails__to_create_new_user(self):
        user = User.signup('name1','email1@email.com','password1', '')
        db.session.add(user)

        with self.assertRaises(Exception): 
            try: 
                User.signup('name1', 'email1@email.com', 'password1', '')
                db.session.flush() 
            
            except IntegrityError: 
                db.session.rollback()
                raise Exception


    # Does User.authenticate successfully return a user when given a valid username and password?
    def test_user_authenticate_succesffully(self):
        username = 'name1'
        email = 'email1.@email.com'
        password = 'password1'
        User.signup(username, email, password, '')
        db.session.commit() 

        user = User.authenticate(username, password)
        self.assertIsInstance(user, User)

    # Does User.authenticate fail to return a user when the username is invalid?
    def test_user_authenticate_fails_bad_username(self):
        username = 'name1'
        email = 'email1.@email.com'
        password = 'password1'
        User.signup(username, email, password, '')
        db.session.commit() 

        username = '1eman'
        user = User.authenticate(username, password)
        self.assertFalse(user)

    # Does User.authenticate fail to return a user when the password is invalid?
    def test_user_authenticate_fails_bad_password(self):
        username = 'name1'
        email = 'email1.@email.com'
        password = 'password1'
        User.signup(username, email, password, '')
        db.session.commit() 

        password = '1drowssap'
        user = User.authenticate(username, password)
        self.assertFalse(user)
