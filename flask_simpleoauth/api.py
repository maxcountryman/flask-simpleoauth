from flask import Blueprint, jsonify

from .model import User
from .oauth_utils import oauth_required

api = Blueprint('api', __name__)


@api.route('/me')
@oauth_required
def me():
    user = User.objects.with_id(g.token.user_id)
    return jsonify({'login': user.login})
