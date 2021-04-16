"""Message model tests."""

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


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_message_created_from_valid_data(self):
        user = User.signup('name1', 'email1@email.com', 'password1', '')
        db.session.commit() 

        message = Message(text='This is a message', user_id=user.id)
        db.session.add(message)
        db.session.commit()

        self.assertIsNotNone(message.id)


    def test_message_not_created_from_bad_user_id(self):

        message = Message(text='This is a message', user_id=10312)

        with self.assertRaises(IntegrityError): 
            db.session.add(message)
            db.session.commit()
            db.session.flush() 
        
        db.session.rollback()

    def test_message_not_created_from_null_text(self):
        user = User.signup('name1', 'email1@email.com', 'password1', '')
        db.session.commit() 

        message = Message(user_id=user.id)

        with self.assertRaises(Exception): 
            db.session.add(message)
            db.session.commit()
            db.session.flush()
        
        db.session.rollback()
    