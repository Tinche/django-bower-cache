from __future__ import absolute_import

import json
import tempfile
import envoy
from os import path
import shutil

from ._compat import mock

from registry.models import Package

from django.conf import settings
from django.test.utils import override_settings
from django.test import TestCase
from django.core.urlresolvers import reverse


@override_settings(DATABASES=
        {'default': {'ENGINE': 'django.db.backends.sqlite3', 
                     'NAME': '.test_db'}})
class PackagesListViewTests(TestCase):

    def test_returns_list_of_packages(self):
        Package.objects.create(name="ember", url="/foo")
        Package.objects.create(name="moment", url="/bar")
        url = reverse("list")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        results = json.loads(response.content.decode())
        self.assertEqual(2, len(results))
        self.assertEqual(results[0]['url'], u'/foo')
        self.assertEqual(results[0]['name'], u'ember')
        self.assertEqual(results[1]['url'], u'/bar')
        self.assertEqual(results[1]['name'], u'moment')


class PackagesFindViewTests(TestCase):
    """Tests for retrieving an individual package."""

    def setUp(self):
        temp_repo_root = tempfile.mkdtemp()
        settings.REPO_ROOT = temp_repo_root

    def tearDown(self):
        shutil.rmtree(settings.REPO_ROOT)

    def test_returns_package_by_name(self):
        Package.objects.create(name="ember", url="/foo")
        url = reverse("find", kwargs={'name': 'ember'})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        self.assertEqual(result['url'], u'/foo')
        self.assertEqual(result['name'], u'ember')

    def test_returns_cloned_repo_by_name(self):
        """Test proper handling of existent cloned repos."""
        # Need to set up a git repo with origin info.
        full_path = path.join(settings.REPO_ROOT, 'test')
        envoy.run('git init {0}'.format(full_path))
        fake_origin = 'git://localhost'
        envoy.run('git -C {0} remote add origin {1}'.format(full_path,
                                                            fake_origin))
        url = reverse("find", kwargs={'name': 'test'})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        expected_url = settings.REPO_URL + u'test'
        self.assertEqual(result['url'], expected_url)
        self.assertEqual(result['name'], u'test')

    def test_returns_cloned_repo_by_name_auto_host(self):
        """Test proper handling of existent cloned repos.

        The settings.REPO_URL option isn't set, so we'll parse the host info
        from the request.
        """
        # Need to set up a git repo with origin info.
        full_path = path.join(settings.REPO_ROOT, 'test')
        envoy.run('git init {0}'.format(full_path))
        fake_origin = 'git://localhost'
        envoy.run('git -C {0} remote add origin {1}'.format(full_path,
                                                            fake_origin))
        url = reverse("find", kwargs={'name': 'test'})

        del settings.REPO_URL

        response = self.client.get(url, HTTP_HOST='test-host')

        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        expected_url = 'git://test-host/test'
        self.assertEqual(result['url'], expected_url)
        self.assertEqual(result['name'], u'test')

    @mock.patch('registry.bowerlib.get_package')
    def test_unknown_nonexistent(self, get_package):
        # Mock the bowerlib.get_package method to avoid I/O
        # We pretend Bower has never heard of 'wat'
        get_package.return_value = None

        Package.objects.create(name="ember", url="/foo")
        url = reverse("find", kwargs={'name': 'wat'})

        response = self.client.get(url)

        self.assertEqual(404, response.status_code)
        upstream = settings.UPSTREAM_BOWER_REGISTRY
        get_package.assert_called_once_with(upstream, 'wat')

    @mock.patch('registry.tasks.clone_repo')
    @mock.patch('registry.bowerlib.get_package')
    def test_returns_503_when_package_name_not_found(self, get_package, clone):
        """Test the find API when we have to fetch from upstream."""
        from registry.tasks import TimeoutError
        # Mock the bowerlib.get_package method to avoid I/O
        # We pretend Bower knows what 'wat' is and a task has been dispatched
        # to clone it.
        get_package.return_value = {'name': 'wat', 'url': 'git://a-url.git'}

        # Mock the clone_repo task dispatch; throw an exception so we don't
        # wait.
        task = mock.MagicMock()
        clone.delay.return_value = task
        task.get.side_effect = TimeoutError()

        Package.objects.create(name="ember", url="/foo")
        url = reverse("find", kwargs={'name': 'wat'})

        response = self.client.get(url)

        self.assertEqual(503, response.status_code)

        upstream = settings.UPSTREAM_BOWER_REGISTRY
        get_package.assert_called_once_with(upstream, 'wat')

        clone.delay.assert_called_once_with('wat', 'git://a-url.git')

    def test_returns_package_when_name_includes_hyphen(self):
        Package.objects.create(name="ember-data", url="/foo")
        url = reverse("find", kwargs={'name': 'ember-data'})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        self.assertEqual(result['url'], u'/foo')
        self.assertEqual(result['name'], u'ember-data')


@override_settings()
class PackagesSearchViewTests(TestCase):

    def setUp(self):
        temp_repo_root = tempfile.mkdtemp()
        settings.REPO_ROOT = temp_repo_root

    def tearDown(self):
        shutil.rmtree(settings.REPO_ROOT)

    def test_returns_list_of_packages_when_search_finds_match(self):
        Package.objects.create(name="ember", url="/foo")
        url = reverse("search", kwargs={'name': 'mbe'})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        results = json.loads(response.content.decode())
        self.assertEqual(1, len(results))
        self.assertEqual(results[0]['url'], u'/foo')
        self.assertEqual(results[0]['name'], u'ember')

    def test_returns_empty_list_when_search_finds_no_match(self):
        Package.objects.create(name="ember", url="/foo")
        url = reverse("search", kwargs={'name': 'wat'})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual('[]', response.content.decode())

    def test_returns_list_of_packages_when_name_includes_hyphen(self):
        Package.objects.create(name="ember-data", url="/foo")
        url = reverse("search", kwargs={'name': 'ember-da'})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        results = json.loads(response.content.decode())
        self.assertEqual(1, len(results))
        self.assertEqual(results[0]['url'], u'/foo')
        self.assertEqual(results[0]['name'], u'ember-data')
