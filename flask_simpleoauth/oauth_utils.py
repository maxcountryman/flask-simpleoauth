from flask import g, jsonify, redirect, request
from rauth.oauth1 import sign

from functools import wraps
from hashlib import md5
from random import randint
from time import time

from .model import AccessToken, Consumer, RequestToken

# TODO:
#
# Parameterize `g` attributes so that these functions become more
# generalized.


def gather_oauth_params(request):
    oauth_params = {}
    req_kwargs = {}
    for key, value in request.values.items():
        if key.startswith('oauth_') and key != 'oauth_signature':
            oauth_params[key] = value
        elif key != 'oauth_signature':
            req_kwargs[key] = value
    return oauth_params, req_kwargs


def verify_oauth_request(request,
                         consumer_key,
                         oauth_token=None,
                         oauth_token_secret=None):
    consumer = Consumer.objects(key=consumer_key).first()
    if consumer is None:
        return {'error': 'oauth_consumer_key'}

    oauth_params, req_kwargs = gather_oauth_params(request)

    timestamp = oauth_params['oauth_timestamp']
    if consumer.last_timestamp > timestamp:
        return {'error': 'oauth_timestamp'}

    nonce = oauth_params['oauth_nonce']
    nonce_timestamp_hash = md5(nonce + str(timestamp)).hexdigest()
    if nonce_timestamp_hash in consumer.previous_requests:
        return {'error': 'oauth_nonce'}

    # We need to store the hashed nonce and timestamp if and only if the
    # provided timestamp is in the still future. If it's not, we can safely
    # ignore this step as we won't accept timestamps from the past in any
    # event.
    consumer.last_timestamp = time()
    if timestamp > consumer.last_timestamp:
        consumer.previous_requests.append(nonce_timestamp_hash)

    consumer.save()

    signed = sign(req_kwargs,
                  request.url,
                  request.method,
                  consumer.key,
                  consumer.secret,
                  access_token=oauth_token,
                  access_token_secret=oauth_token_secret,
                  oauth_params=oauth_params)

    their_signature = request.values.get('oauth_signature')
    our_signature = signed['oauth_signature']

    if our_signature != their_signature:
        return {'error': 'oauth_signature'}


def create_request_token(request):
    oauth_callback = request.values.get('oauth_callback')

    token = RequestToken(consumer_key=g.consumer_key,
                         oauth_callback=oauth_callback)
    token.save()

    return {'oauth_token': token.oauth_token,
            'oauth_token_secret': token.oauth_token_secret,
            'oauth_callback_confirmed': True}


def _generate_verifier(size=7):
    return ''.join(str(randint(0, 9)) for i in range(size))


def verify_request_token(request):
    user_verified = bool(request.values.get('verified', 0))

    request_token = request.values.get('oauth_token')

    token = RequestToken.objects(oauth_token=request_token).first()
    if token is None:
        return {'error': 'oauth_token'}

    token.oauth_verifer = _generate_verifier()
    token.save()

    if token.callback is not None:
        if user_verified:
            params = {'oauth_token': token.oauth_token,
                      'oauth_verifier': token.oauth_verifier,
                      'user_id': g.user.id}
            return redirect(token.callback, params=params)

        token.delete()
        return redirect(token.callback)

    token.oauth_verifier = _generate_verifier()
    token.save()

    if user_verified:
        return {'oauth_verifier': token.oauth_verifier}

    token.delete()
    return {'error': 'denied'}


def create_access_token(request):
    req_token = RequestToken.objects(oauth_token=g.oauth_token,
                                     oauth_verifier=g.oauth_verifier).first()

    if req_token is None:
        return {'error': 'oauth_token'}

    consumer = Consumer.objects(consumer_key=g.consumer_key).first()

    if consumer is None:
        return {'error': 'no such consumer application'}

    token = AccessToken.objects(user_id=req_token.user_id,
                                consumer_id=consumer.id)
    token.save()
    req_token.delete()

    return {'oauth_token': token.oauth_token,
            'oauth_token_secret': token.oauth_token_secret,
            'user_id': token.user_id}


def oauth_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        g.token = None

        g.consumer_key = request.values.get('oauth_consumer_key')
        g.oauth_token = request.values.get('oauth_token')
        g.oauth_verifier = request.values.get('oauth_verifier')

        if g.oauth_verifier is not None:
            token = \
                RequestToken.objects(oauth_token=g.oauth_token,
                                     oauth_verifier=g.oauth_verifier).first()
            if token.is_expired():
                return jsonify({'error': 'request token expired'})
        elif g.oauth_token is not None:
            token = AccessToken.objects(oauth_token=g.oauth_token)
            g.token = token

        verify_args = (request, g.consumer_key)

        if g.token is not None:
            verify_args += (g.oauth_token, token.oauth_token_secret)

        error = verify_oauth_request(*verify_args)
        if error is None:
            return f(*args, **kwargs)
        return jsonify(error)
    return decorator
