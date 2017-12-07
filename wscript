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


def options(opt):
    pass

def configure(conf):

    # Ensure that the waf-light program is available in the in the
    # waf folder. This is used to build the waf binary.
    doxyrest_path = os.path.join(conf.dependency_path('doxyrest'),
        'doxyrest-linux-1.1.0-amd64', 'bin')

    conf.find_program('doxyrest', exts='',
                      path_list=[doxyrest_path])


    conf.find_program('doxygen')




def build(bld):
    pass
