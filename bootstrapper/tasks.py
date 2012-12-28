import os
import sys

from fabric.api import local, sudo, task, parallel, show
from fabric.api import reboot as _reboot
from fabric.contrib import files

from bootstrapper import lowlevel
from bootstrapper.config import verbose
from bootstrapper.helpers import puts, has, runner, requires_configuration, requires_host

# expose this task
hostname = lowlevel.hostname

############################# HIGH-LEVEL FUNCTIONS ##############################
@task
@parallel
@requires_host
def delete_salt():
    verbose()
    runner.silent('apt-get purge salt-minion salt-master')
    runner.silent('rm -rf /etc/salt /opt/salt /opt/saltstack /var/log/salt', use_sudo=True)
    runner.silent('rm -f /usr/local/bin/salt-*', use_sudo=True)

@task
@parallel
@requires_host
def reboot():
    runner.action('Rebooting')
    _reboot()
    runner.action('Done')

@task
@parallel
@requires_host
@requires_configuration
def setup_master(and_minion=1, upgrade=1):
    """Bootstraps and sets up a master.

    Sets up a minion pointing to itself unless otherwise said.
    """
    lowlevel.bootstrap(upgrade)
    lowlevel.master()
    lowlevel.upload(sync=False)
    if int(and_minion):
        name = hostname()
        lowlevel.create_minion_key(name)
        lowlevel.minion(master='127.0.0.1', hostname=name)


@task
@parallel
@requires_host
@requires_configuration
def setup_minion(master, upgrade=1):
    "Bootstraps and sets up a minion. Requires the ip address of the master."
    lowlevel.bootstrap(upgrade)
    lowlevel.minion(master)


@task
@parallel
@requires_host
@requires_configuration
def deploy(filter='*', upload=1, debug=0):
    """Tells master to send pillars and execute salt state files on clients.

    If debug is set to true, runs locally with more debugging information output.
    If upload is set to true, then uploads current salt configurations to the master before deploying.
    """
    runner.action('Deploying salt files')
    output = ''
    with runner.with_prefix('  '):
        if has('/opt/saltstack/', 'test -e %(app)s'):
            lowlevel.upgrade_bleeding()
        if int(upload):
            lowlevel.upload()
        if int(debug):
            cmd = "salt-call state.highstate -l debug"
        else:    
            cmd = "salt '{0}' state.highstate".format(filter)
        runner.action('Ensuring minion state')
        with open('sync.log', 'w+') as handle:
            runner.sudo(cmd, combine_stderr=True, stdout=handle)

