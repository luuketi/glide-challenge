import datetime
from flask import request
from flask_restplus import Resource, Api

from src import blueprint
from src.dto import *
from src.models import Offices, Departments


api = Api(blueprint,
          title='Big Corp API',
          version='1.0'
          )


@api.route('/offices/<int:id>')
class OfficeDetail(Resource):

    def get(self, id):
        print(Offices.get_by_id(id))

@api.route('/offices')
class OfficeList(Resource):

    def get(self):
        print('list')


@api.route('/departments/<int:id>')
class DepartmentDetail(Resource):

    def get(self, id):
        print(request.values.getlist('expand'))
        Departments.get_by_id(id)




@api.route('/departments')
class DepartmentList(Resource):

    def get(self):
        print('list')


#class Departments(Resource)





'''
class BaseResource(Resource):

    def _return_error_message(self, error_string, error_code):
        """Returns a error message in json format"""
        return {'status': 'fail', 'message': error_string}, error_code

    def _get_user_by(self, username=None, user_id=None):
        """Returns the user from model"""
        if username:
            return User.find_by_username(username)
        if user_id:
            return User.find_by_id(user_id)


@api.route('/users')
class Users(BaseResource):

    @api.response(200, '')
    @api.response(409, 'User already exists.')
    @api.doc('createUser')
    @use_kwargs(UserSchema())
    def post(self, username, password):
        """Create a user in the system."""

        if self._get_user_by(username=username):
            return self._return_error_message('User already exists. Please Log in.', 409)

        new_user = User(username=username, password=password).save()
        return {'id': new_user.id}, 200


@api.route('/login')
class Login(BaseResource):

    @api.response(200, '')
    @api.response(401, 'Unauthorized')
    @use_kwargs(UserSchema())
    def post(self, username, password):
        """Log in as an existing user."""

        current_user = self._get_user_by(username=username)
        if not current_user:
            return self._return_error_message("User {} doesn't exist".format(username), 401)

        # return token if password matches
        if current_user.check_password(password):
            access_token = create_access_token(identity=username)
            return {'id': current_user.id, 'token': access_token}
        else:
            return self._return_error_message('User already exists. Please Log in.', 401)


@api.route('/logout')
class Logout(BaseResource):

    @jwt_required
    def post(self):
        """Log out an existing user."""
        jti = get_raw_jwt()['jti']
        try:
            RevokedToken(jti=jti).save()
            return {'message': 'Access token has been revoked.'}
        except Exception:
            return self._return_error_message('Wrong credentials.', 500)


@api.route('/messages')
class Messages(BaseResource):

    @api.response(200, '')
    @api.response(400, 'Sender/Receiver not found')
    @api.doc('sendMessage')
    @use_args(MessageSchema())
    @jwt_required
    def post(self, message):
        """Send a message from one user to another."""

        sender = self._get_user_by(user_id=message.sender)
        recipient = self._get_user_by(user_id=message.recipient)
        if not sender or not recipient:
            return self._return_error_message("Sender/Receiver not found.", 400)

        new_message = Message(
            sender_id=message.sender,
            recipient_id=message.recipient,
            timestamp=datetime.datetime.utcnow(),
            content=message.content,
        ).save()

        return {'id': new_message.id, 'timestamp': new_message.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")}, 200

    args = {
        'recipient': fields.Int(required=True),
        'start': fields.Int(required=True),
        'limit': fields.Int(missing=100),
    }

    @api.response(200, '')
    @api.doc('getMessages')
    @use_kwargs(args)
    @jwt_required
    def get(self, recipient, start, limit):
        """Fetch all existing messages to a given recipient, within a range of message IDs."""
        messages = Message.get_messages(recipient, start, limit)
        return MessagesSchema().dump({'messages': messages})


@api.route('/check')
class Check(BaseResource):

    @api.response(200, '')
    def post(self):
        """Check the health of the system."""
        if self.query_health() != 1:
            raise Exception('unexpected query result')
        return {"health": "ok"}, 200

    def query_health(self):
        with db.engine.connect() as conn:
            result = conn.execute("SELECT 1")
            (res,) = result.fetchone()
            return res
'''
