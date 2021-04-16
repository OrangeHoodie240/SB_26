"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, Message, User

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

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_gets_message(self):
        user = User(username='name1', email='email1@email.com',
                    password='password1')
        db.session.add(user)
        db.session.commit()

        message = Message(text='Here is some neat text', user_id=user.id)
        db.session.add(message)
        db.session.commit()

        with self.client as c:
            resp = c.get(f'/messages/{message.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(message.text, html)

    def test_deletes_message(self):
        user = User(username='name1', email='email1@email.com',
                    password='password1')
        db.session.add(user)
        db.session.commit()

        message = Message(text='Here is some neat text', user_id=user.id)
        db.session.add(message)
        db.session.commit()

        message_id = message.id

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = user.id
            resp = c.post(f'/messages/{message.id}/delete')

            self.assertEqual(resp.status_code, 302)

            message = Message.query.filter(
                Message.id == message_id).one_or_none()
            self.assertIsNone(message)


# When you’re logged out, are you prohibited from adding messages?


    def test_cant_add_message_logged_out(self):
        count_before = Message.query.count()
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)

            count_after = Message.query.count()
            self.assertEqual(count_before, count_after)


# When you’re logged out, are you prohibited from deleting messages?

    def test_cant_delete_message_logged_out(self):
        user = User(username='name1', email='email1@email.com',
                    password='password1')
        db.session.add(user)
        db.session.commit()

        message = Message(text='Here is some neat text', user_id=user.id)
        db.session.add(message)
        db.session.commit()

        count_before = Message.query.count()

        with self.client as c:
            resp = c.post(f'/messages/{message.id}/delete')

            self.assertEqual(resp.status_code, 302)

            count_after = Message.query.count()
            self.assertEqual(count_before, count_after)

# When you’re logged in, are you prohibiting from deleting a message as another user?
    def test_cant_delete_message_other_users_message(self):
        user = User(username='name1', email='email1@email.com',
                    password='password1')
        db.session.add(user)
        db.session.commit()

        message = Message(text='Here is some neat text', user_id=user.id)
        db.session.add(message)
        db.session.commit()

        message_id = message.id
        count_before = Message.query.count() 
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = c.post(f'/messages/{message.id}/delete')

            self.assertEqual(resp.status_code, 302)
            count_after = Message.query.count() 

            self.assertEqual(count_before, count_after)