from setuptools import find_packages, setup
setup(
    name='todoist-todotxt-migration',
    packages=find_packages(include=['todoist_todotxt_migration']),
    version='0.2.4',
    description='My first Python library',
    author='Me',
    license='MIT',
    install_requires=['todoist-api-python']
)
