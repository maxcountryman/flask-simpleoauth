from wtforms import Form, TextField, PasswordField, validators


class ConsumerForm(Form):
    name = TextField('App Name', [validators.Required(),
                                  validators.Length(min=6, max=32)])

    callback_uri = TextField('Callback', [validators.Optional()])


class LoginForm(Form):
    login = TextField('Login', [validators.Required(),
                                validators.Length(min=6, max=32)])

    password = PasswordField('Password', [validators.Required()])


class UserForm(Form):
    login = TextField('Login', [validators.Required(),
                                validators.Length(min=6, max=32)])
    password = \
        PasswordField('Password',
                      [validators.Required(),
                       validators.Length(min=6, max=265),
                       validators.EqualTo('confirm',
                                          message='Passwords do not match!')])

    confirm = PasswordField('Confirm Password',
                            [validators.Required(),
                             validators.Length(min=6, max=265)])
