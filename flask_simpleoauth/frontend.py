from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)

from .form import ConsumerForm, LoginForm, UserForm
from .model import Consumer, User
from .utils import login_required

frontend = Blueprint('frontend', __name__)


@frontend.route('/')
def index():
    return render_template('index.html')


@frontend.route('/user/new/', methods=['GET', 'POST'])
def new_user():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(login=form.login.data)
        user.set_password(form.password.data)
        user.save()
        flash('User created')
        return redirect(url_for('.index'))
    return render_template('new_user.html', form=form)


@frontend.route('/login/', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next_url', url_for('.index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.objects(login=form.login.data).first()
        if user is not None and user.check_password(form.password.data):
            session['user_id'] = user.id
            return redirect(next_url)
    return render_template('login.html', form=form)


@frontend.route('/logout/')
def logout():
    next_url = request.args.get('next_url', url_for('.login'))
    session.pop('login')
    return redirect(next_url)


@frontend.route('/apps/new/', methods=['GET', 'POST'])
@login_required
def apps_new():
    '''Registers a new OAuth consumer application with the provider.'''
    form = ConsumerForm(request.form)
    if request.method == 'POST' and form.validate():
        consumer = Consumer(name=form.name.data,
                            callback_uri=form.callback_uri.data)
        consumer.save()
        g.user.owned_consumers.append(consumer.id)
        g.user.save()
        args = {'key': consumer.key, 'secret': consumer.secret}
        flash('Consumer created. Key {key} Secret {secret}'.format(**args))
    owned_consumers = []
    for consumer_id in g.user.owned_consumers:
        consumer = Consumer.objects.with_id(consumer_id)
        owned_consumers.append(consumer)
    return render_template('new_app.html',
                           form=form,
                           owned_consumers=owned_consumers)
