# Flask-SimpleOAuth

Presenting a simple Flask OAuth 1.0a provider built on
[rauth](https://github.com/litl/rauth)'s battle-tested signing logic.

Because OAuth doesn't have to be hard...


## Setup

You're going to need MongoDB setup on your platform. If you're using OS X and
brew you could do this:

```sh
$ brew install mongo
```

Once you've got MongoDB the necessary Python packages can be installed like so:

```sh
$ pip install -r requirements.txt
```

Okay you're all set. You can run it now, with any luck:

```sh
$ python runner.py
```

Now visit [http://localhost:5000/user/new](http://localhost:5000/user/new) in
your browser and get to work...you probably also want to set up a consumer app
here: [http://localhost:5000/apps/new](http://localhost:5000/apps/new).


## Rationale

Flask-SimpleOAuth is opinioated because OAuth providers generally need to make
assumptions about things like user models. This makes providers a tough nut to
abstract. For this reason, I've created this as a demonstration of what's
possible and to maybe also give you a foundation for your own projects.

The idea here is to show you how you could organize a Flask project to support
OAuth and demonstrate how easy it is to is to use rauth's robust signing logic
outside of its client scope. (In the future, look for this to be split out into
its own package.)

For these reasons, the frontend, the models, and anything else that wasn't
essential to "making it work" was left fairly barren. I want to leave these
rough edges as an open invitation for others to round out their own
implementations. And I hope that things like the MongoEngine documents might
be, with minimal pain, swapped out for whatever you like.


## Disclaimer

This is a work-in-progress and significant changes may occur without notice.
