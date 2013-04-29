from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)

from .model import Consumer, RequestToken
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
    req_token = request.values.get('oauth_token')
    if req_token is None:
        flash('Missing token')
        return redirect(url_for('frontend.index'))

    token = RequestToken.objects(oauth_token=req_token).first()
    consumer = Consumer.objects(key=token.consumer_key).first()
    if request.method == 'POST':
        return jsonify(verify_request_token(request))
    return render_template('authorize.html', consumer=consumer)


@oauth.route('/access_token', methods=['POST'])
@oauth_required
def access_token():
    return jsonify(create_access_token(request))
