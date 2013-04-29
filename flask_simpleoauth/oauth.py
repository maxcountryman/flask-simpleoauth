from flask import Blueprint, jsonify, render_template, request

from .oauth_utils import (create_access_token, create_request_token,
                          oauth_required, verify_request_token)
from .utils import login_required

oauth = Blueprint('oauth', __name__)


@oauth.route('/request_token')
@oauth_required
def request_token():
    return jsonify(create_request_token(request))


@oauth.route('/authorize', methods=['GET', 'POST'])
@login_required
def authorize():
    if request.method == 'POST':
        return jsonify(verify_request_token(request))
    return render_template('authorize.html')


@oauth.route('/access_token', methods=['POST'])
@oauth_required
def access_token():
    return jsonify(create_access_token(request))
