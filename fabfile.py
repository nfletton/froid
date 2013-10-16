import os

from fabric.api import env
from fabric.contrib.project import rsync_project
from fabric.operations import local
from website import app
from website.freeze import freezer

import settings

def freeze():
    urls = freezer.freeze()
    print 'Built %i files.' % len(urls)


def run():
    app.run(debug=True)


def dry_run():
    deploy(dry_run='yes')


def deploy(dry_run='no'):
    rsync_project(remote_dir=env.remote_dir,
                  local_dir=env.local_dir + '/',
                  delete=True,
                  extra_opts='--dry-run' if dry_run == 'yes' else '')


def clean():
    if os.name == 'posix':
        local('rm -r ' + env.local_dir)
        local('mkdir ' + env.local_dir)
    else:
        local('rmdir /s /q ' + env.local_dir)
        local('mkdir ' + env.local_dir)

if __name__ == '__main__':
    run()
