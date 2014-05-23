"""Unit tests for the models."""
from registry.models import ClonedRepo, Package


def test_cloned_repo_as_package():
    """Test the cloned repo model converting itself into a package."""
    pkg_name = 'aname'
    repo_url = 'http://test/'

    cloned_repo = ClonedRepo(name=pkg_name, origin='git://test.git')

    pkg = cloned_repo.to_package(repo_url)

    assert isinstance(pkg, Package)
    assert pkg.name == pkg_name
    assert pkg.url == repo_url + "aname"