from fabric.api import env

env.hosts = ['myuser@mysite.com']
env.local_dir = 'public'
env.remote_dir = 'temp'

