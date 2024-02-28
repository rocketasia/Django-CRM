#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#


def get_version(version, repo_dir=None, as_semver=False):
    """
    Returns a "PEP 386-compliant" or "Semantic Versioning 2.0.0" version
    number from VERSION.
    """
    version = get_complete_version(version)

    # Now build the two parts of the "PEP 386-compliant" version number:
    # major = "X.Y[.Z]""
    # sub = ".devN" - for pre-alpha releases
    #     | "{a|b|c}N" - for alpha, beta and rc releases
    # Or build the two parts of the "Semantic Versioning 2.0.0" version:
    # major = "X.Y.Z"
    # sub = "-{alpha|beta|rc}.N" - for alpha, beta and rc releases.

    major = get_major_version(version, as_semver=as_semver)

    sub = ''
    if version[3] == 'alpha' and not version[4]:
        changeset = get_vcs_changeset(repo_dir) or '19700101000000'
        if as_semver:
            sub = '-alpha.%s' % changeset
        else:
            sub = '.dev%s' % changeset
    elif version[3] != 'final':
        if as_semver:
            sub = '-%s.%s' % (version[3], str(version[4]))
        else:
            mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
            sub = mapping[version[3]] + str(version[4])

    return str(major + sub)


def get_docs_version(version):
    version = get_complete_version(version)
    if version[3] != 'final':
        return 'dev'
    else:
        return '%d.%d' % version[:2]


def get_major_version(version, as_semver=False):
    """
    Returns major version from VERSION.
    """
    version = get_complete_version(version)
    parts = 2 if version[2] == 0 and not as_semver else 3
    major = '.'.join(str(x) for x in version[:parts])
    return major


def get_complete_version(version):
    """
    Returns a tuple of the version. If version argument is non-empty,
    then checks for correctness of the tuple provided.
    """
    if not version:
        return (0, 0, 1, 'alpha', 0)
    assert len(version) == 5
    assert version[3] in ('alpha', 'beta', 'rc', 'final')
    return version


def get_vcs_changeset(repo_dir):
    """
    Returns a numeric identifier of the latest VCS changeset.
    """
    from subprocess import Popen, PIPE
    from datetime import datetime

    if not repo_dir:
        from os.path import dirname, abspath
        repo_dir = dirname(dirname(abspath(__file__)))
    commands = (
        'git log --pretty=format:%ct --quiet -1 HEAD',
        'hg tip --template "{date|hgdate}"',
    )
    for command in commands:
        log = Popen(command, stdout=PIPE, stderr=PIPE,
                    shell=True, cwd=repo_dir, universal_newlines=True)
        stamp = log.communicate()[0]
        try:
            stamp = stamp.split(' ')[0]
            stamp = datetime.utcfromtimestamp(int(stamp))
        except ValueError:
            stamp = None
        else:
            break
    return stamp.strftime('%Y%m%d%H%M%S') if stamp else None
