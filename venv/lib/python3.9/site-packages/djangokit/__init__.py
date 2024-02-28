#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
"""A set of extensions for Django used in the construction of complex web
applications.
"""
import os
from djangokit.utils import version

# The version (X, Y, Z, R, N) builds by next rules:
# Variables X, Y, Z & N must be integers. R - can be 'alpha', 'beta' 'rc' or
# 'final' string. R == 'alpha' and N > 0 it is pre-alpha release.
# version = X.Y[.Z]
# subversion = .devN - for pre-alpha releases
#            | {a|b|c}N - for 'alpha', 'beta' and 'rc' releases
# subversion is not exists for 'final' release.
VERSION = (0, 13, 0, 'final', 0)


def get_version():
    path = os.path.dirname(os.path.abspath(__file__))
    return version.get_version(VERSION, path)


__version__ = get_version()
