# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os

c = get_config()

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

from tornado import gen
from dockerspawner import DockerSpawner

class DockerSpawner_host(DockerSpawner):
        
    def set_free_port(self):
        import socket
        s = socket.socket()
        s.bind(('', 0))
        port = s.getsockname()[1]
        s.close()
        self.port = port
        return

    @gen.coroutine
    def get_ip_and_port(self):
        return self.host_ip, self.port
    
    @gen.coroutine
    def create_object(self):
        """Create the container/service object"""
        # image priority:
        # 1. user options (from spawn options form)
        # 2. self.image from config
        image_option = self.user_options.get('image')
        if image_option:
            # save choice in self.image
            self.image = yield self.check_image_whitelist(image_option)

        create_kwargs = dict(
            image=self.image,
            environment=self.get_env(),
            volumes=self.volume_mount_points,
            name=self.container_name,
            command=(yield self.get_command()),
        )

        self.set_free_port()
        # ensure internal port is exposed
        create_kwargs["ports"] = {"%i/tcp" % self.port: None}

        create_kwargs.update(self.extra_create_kwargs)

        create_kwargs["command"] += ' --ip=' + self.host_ip + ' --port=' + str(self.port)


        # build the dictionary of keyword arguments for host_config
        host_config = dict(binds=self.volume_binds, links=self.links)

        if getattr(self, "mem_limit", None) is not None:
            # If jupyterhub version > 0.7, mem_limit is a traitlet that can
            # be directly configured. If so, use it to set mem_limit.
            # this will still be overriden by extra_host_config
            host_config["mem_limit"] = self.mem_limit

        if not self.use_internal_ip:
            host_config["port_bindings"] = {self.port: (self.host_ip,)}
        host_config.update(self.extra_host_config)
        host_config.setdefault("network_mode", self.network_name)

        self.log.debug("Starting host with config: %s", host_config)

        host_config = self.client.create_host_config(**host_config)
        create_kwargs.setdefault("host_config", {}).update(host_config)

        # create the container
        obj = yield self.docker("create_container", **create_kwargs)
        return obj



# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = DockerSpawner_host
# Spawn containers from this image
c.DockerSpawner_host.image = os.environ['DOCKER_NOTEBOOK_IMAGE']
# JupyterHub requires a single-user instance of the Notebook server, so we
# default to using the `start-singleuser.sh` script included in the
# jupyter/docker-stacks *-notebook images as the Docker run command when
# spawning containers.  Optionally, you can override the Docker run command
# using the DOCKER_SPAWN_CMD environment variable.
spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD', "start-notebook.sh")

# cross-origin requests
origin = '*'

c.JupyterHub.tornado_settings = {
    'headers': {
        'Access-Control-Allow-Origin': origin,
    },
}
c.DockerSpawner_host.args = [f'--NotebookApp.allow_origin=*']

extra_create_kwargs = {
    'command': spawn_cmd,
}
extra_host_config = {
    'network_mode': 'host',
    'runtime': 'nvidia',
    'restart_policy': {'Name': 'always'}
}

c.DockerSpawner_host.extra_create_kwargs.update(extra_create_kwargs)
# Connect containers to this Docker network
c.DockerSpawner_host.use_internal_ip = False
c.DockerSpawner_host.network_name = 'host'
# Pass the network name as argument to spawned containers
c.DockerSpawner_host.extra_host_config.update(extra_host_config)
# Explicitly set notebook directory because we'll be mounting a host volume to
# it.
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/hit605'
c.DockerSpawner_host.notebook_dir = notebook_dir
# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
c.DockerSpawner_host.volumes = { 'jupyterhub-user-{username}': notebook_dir }
# volume_driver is no longer a keyword argument to create_container()
# c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })
# Remove containers once they are stopped
c.DockerSpawner_host.remove_containers = True
# For debugging arguments passed to spawned containers
#c.DockerSpawner.debug = True
c.DockerSpawner_host.host_ip = '0.0.0.0'

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_connect_ip = '0.0.0.0'
c.JupyterHub.hub_port = 8081

# TLS config
c.JupyterHub.ip = ''
c.JupyterHub.port = 8000
c.JupyterHub.ssl_key = os.environ['SSL_KEY']
c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

# Authenticate users with GitHub OAuth
c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']

# Persist hub data on volume mounted inside container
data_dir = os.environ.get('DATA_VOLUME_CONTAINER', '/data')

c.JupyterHub.cookie_secret_file = os.path.join(data_dir,
    'jupyterhub_cookie_secret')

# Whitlelist users and admins
#c.Authenticator.whitelist = whitelist = set()
c.Authenticator.admin_users = admin = set()
c.JupyterHub.admin_access = True
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'userlist')) as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        # in case of newline at the end of userlist file
        if len(parts) >= 1:
            name = parts[0]
            #whitelist.add(name)
            if len(parts) > 1 and parts[1] == 'admin':
                admin.add(name)


