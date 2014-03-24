from fabric.api import env


def production():
    """
    Env parameters for the production environment.
    """

    env.host_string = 'root@5.9.195.3:22'
    env.project_dir = '/var/www/pmgbilltracker'
    env.config_dir = 'config/production'
    env.activate = 'source %s/env/bin/activate' % env.project_dir
    print("PRODUCTION ENVIRONMENT\n")
    return


def staging():
    """
    Env parameters for the staging environment.
    """

    env.host_string = 'root@5.9.195.2:22'
    env.project_dir = '/var/www/pmgbilltracker'
    env.config_dir = 'config/staging'
    env.activate = 'source %s/env/bin/activate' % env.project_dir
    print("STAGING ENVIRONMENT\n")
    return