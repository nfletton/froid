from fabric.api import env

env.hosts = ['zygal@kontar.kattare.com']
env.local_dir = 'public'
env.remote_dir = 'temp'

