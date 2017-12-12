#! /usr/bin/env python
# encoding: utf-8

import os
import sys

import waflib
from waflib.TaskGen import feature

top = '.'


@feature('doxyrest')
def dd(self):

    if not getattr(self, 'doxyfile', None):
        self.generator.bld.fatal('no doxyfile??')

    node = self.doxyfile
    if not isinstance(node, Node.Node):
        node = self.path.find_resource(node)
    if not node:
        raise ValueError('doxygen file not found')

    # the task instance
    dsk = self.create_task('doxygen', node)

DOXYREST = 'doxyrest-linux-1.1.0-amd64'


def resolve(ctx):

    ctx.add_dependency(
        name='doxyrest',
        recurse=False,
        optional=False,
        resolver='http',
        sources=['https://github.com/vovkos/doxyrest/releases/download/doxyrest-1.1.0/doxyrest-linux-1.1.0-amd64.tar.xz'],
        post_resolve=[{"type":"run", "command": "tar xvf doxyrest-linux-1.1.0-amd64.tar.xz"}])

    ctx.add_dependency(
        name='virtualenv',
        recurse=False,
        optional=False,
        resolver='git',
        method='checkout',
        checkout='15.1.0',
        sources=['github.com/pypa/virtualenv.git'])


def options(opt):

    opt.add_option(
        '--run_tests', default=False, action='store_true',
        help='Run all unit tests')

    opt.add_option(
        '--test_filter', default=None, action='store',
        help='Runs all tests that include the substring specified.'
             'Wildcards not allowed. (Used with --run_tests)')

    opt.add_option(
        '--pytest_basetemp', default='pytest',
        help='Set the basetemp folder where pytest executes the tests')


def configure(conf):

    # Ensure that the waf-light program is available in the in the
    # waf folder. This is used to build the waf binary.
    doxyrest_path = os.path.join(conf.dependency_path('doxyrest'),
        'doxyrest-linux-1.1.0-amd64', 'bin')

    conf.find_program('doxyrest', exts='',
                      path_list=[doxyrest_path])


    conf.find_program('doxygen')


def _create_virtualenv(ctx, cwd):
    # Make sure the virtualenv Python module is in path
    venv_path = ctx.dependency_path('virtualenv')

    env = dict(os.environ)
    env.update({'PYTHONPATH': os.path.pathsep.join([venv_path])})

    from waflib.extras.wurf.virtualenv import VirtualEnv
    return VirtualEnv.create(cwd=cwd, env=env, name=None, ctx=ctx,
                             pip_packages_path=os.path.join(ctx.path.abspath(),
                                                            'pip_packages'))


def build(bld):
     if bld.options.run_tests:
        _pytest(bld=bld)


def _pytest(bld):

    venv = _create_virtualenv(ctx=bld, cwd=bld.path.abspath())

    with venv:

        venv.pip_install('pytest', 'mock',
                         'pytest-testdirectory==2.1.0',
                         'pep8', 'pyflakes', 'sphinx')

        venv.env['PATH'] = os.path.pathsep.join(
            [venv.env['PATH'], os.environ['PATH']])

        # We override the pytest temp folder with the basetemp option,
        # so the test folders will be available at the specified location
        # on all platforms. The default location is the "pytest" local folder.
        basetemp = os.path.abspath(os.path.expanduser(
            bld.options.pytest_basetemp))

        # We need to manually remove the previously created basetemp folder,
        # because pytest uses os.listdir in the removal process, and that fails
        # if there are any broken symlinks in that folder.
        if os.path.exists(basetemp):
            waflib.extras.wurf.directory.remove_directory(path=basetemp)

        # Make python not write any .pyc files. These may linger around
        # in the file system and make some tests pass although their .py
        # counter-part has been e.g. deleted
        command = 'python -B -m pytest test --basetemp ' + basetemp


        # Adds the test filter if specified
        if bld.options.test_filter:
            command += ' -k "{}"'.format(bld.options.test_filter)

        venv.run(command)

        # Run PEP8 check
        # bld.msg("Running", "pep8")
        # venv.run('python -m pep8 --filename=*.py,wscript '
        #          'src test wscript buildbot.py')

        # Run pyflakes
        bld.msg("Running", "pyflakes")
        venv.run('python -m pyflakes test')
