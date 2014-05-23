"""REST API views."""
import logging

from django.http import Http404
from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, ListCreateAPIView, \
    GenericAPIView

from .models import Package, ClonedRepo
from .serializers import PackageSerializer
from . import bowerlib, tasks

LOG = logging.getLogger(__name__)


class ServiceUnavailable(APIException):
    """Short-circuit a view and just return the status code."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Try again later"


class PackagesListView(ListCreateAPIView):
    model = Package


class PackagesSearchView(ListAPIView):
    model = Package

    def get_queryset(self):
        search = self.kwargs['name']
        return self.model.objects.filter(name__icontains=search)


class PackagesRetrieveView(APIView):
    serializer_class = PackageSerializer
    DEFAULT_GIT_REPO_PAT = u"git://{0}/"

    def get(self, request, name):
        res = self._get(request, name)
        serializer = self.serializer_class(res)
        return Response(data=serializer.data)

    def _get(self, request, name):
        LOG.info("Get request for package %s." % name)
        try:
            local_repo = ClonedRepo.objects.get(pk=name)
            if hasattr(settings, 'REPO_URL'):
                repo_url = settings.REPO_URL
            else:
                hostname = self._parse_hostname(request.get_host())
                repo_url = self.DEFAULT_GIT_REPO_PAT.format(hostname)
            return local_repo.to_package(repo_url)
        except ClonedRepo.DoesNotExist:
            pass

        try:
            return Package.objects.get(name=name)
        except Package.DoesNotExist:
            pass

        if hasattr(settings, 'REPO_URL'):
            repo_url = settings.REPO_URL
        else:
            repo_url = self._parse_hostname(request.get_host()) + '/'
        return self.clone_from_upstream(name, repo_url)

    @staticmethod
    def _parse_hostname(full_hostname):
        """Try parsing out the hostname without the port.

        To be used on Django request's get_host() output."""
        return full_hostname.split(':')[0]

    @staticmethod
    def clone_from_upstream(pkg_name, repo_url):
        """Clone a non-existent package using the upstream registry."""
        msg = "Spawning a cloning task for %s from upstream due to API req."
        LOG.info(msg % pkg_name)

        upstream_url = settings.UPSTREAM_BOWER_REGISTRY
        upstream_pkg = bowerlib.get_package(upstream_url, pkg_name)

        if upstream_pkg is None:
            raise Http404

        task = tasks.clone_repo.delay(pkg_name, upstream_pkg['url'])
        try:
            result = task.get(timeout=5)
        except tasks.TimeoutError:
            # Not done yet. What to return?
            raise ServiceUnavailable

        return result.to_package(repo_url)
