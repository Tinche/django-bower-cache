## Django Bower Cache (the Python/Django edition)

[![Build Status](https://travis-ci.org/Tinche/django-bower-cache.png)](https://travis-ci.org/Tinche/django-bower-cache)
[![Coverage Status](https://coveralls.io/repos/Tinche/django-bower-cache/badge.png?branch=master)](https://coveralls.io/r/Tinche/django-bower-cache?branch=master)
[![Requirements Status](https://requires.io/github/Tinche/django-bower-cache/requirements.png?branch=master)](https://requires.io/github/Tinche/django-bower-cache/requirements/?branch=master)

Django Bower Cache is a Django app providing two services:

* act as a registry (a name to URL mapper) for Bower packages.
* act as a caching proxy for remote Bower packages.

The admin interface is available for both functionalities.

If you just want a simple way to run a local Bower caching proxy, see the
[Bower Cache](https://github.com/Tinche/bower-cache) project, which is built around Django Bower
Cache.

Django Bower Cache supports Python 2.6, 2.7 and PyPy.

## Settings

Django Bower Cache uses three additional settings from the Django settings file.

`REPO_ROOT` - the absolute path to the directory which will contain the cached
Bower git repositories. Example: `/var/bower-cache`.

`UPSTREAM_BOWER_REGISTRY` - the URL of the Bower index from which to retrieve
package data. Currently the global Bower registry is located at [https://bower.herokuapp.com](https://bower.herokuapp.com).

`REPO_URL` - Optional. The URL hostname and prefix to use when generating git
URLs for cloned repositories. If left unspecified, Django Bower Cache will try
extracting the hostname from the HTTP request and use the root URL path plus
the package name. For example, if Django Bower Cache happens to be queried
at `http://10.1.10.5/` for the Bootstrap package, and the Bootstrap package has
been cached, the generated git URL will be `git://10.1.10.5/bootstrap`.

## Documentation

The documentation will be linked here once it's written.

## License

Copyright © 2013 Toran Billups, Tin Tvrtković.

Licensed under the MIT License.
