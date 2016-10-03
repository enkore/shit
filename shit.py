#!/usr/bin/env python

from collections import Counter
from pathlib import Path
import shlex
import subprocess
import sys

import click

CPE = subprocess.CalledProcessError


def run(args):
    return subprocess.run(shlex.split(args), check=True)


def scrape(args):
    return subprocess.run(shlex.split(args), check=True, stderr=subprocess.DEVNULL, stdout=subprocess.PIPE).stdout.decode().strip()


def repo_name():
    path = scrape('git rev-parse --show-toplevel')
    return Path(path).name


def current_upstream():
    symref = scrape('git symbolic-ref -q HEAD')
    try:
        remote, branch = scrape('git for-each-ref --format="%(upstream:short)" ' + symref).split('/', maxsplit=1)
        return remote
    except (CPE, ValueError):
        click.echo('No upstream configured.')


def current_branch():
    """Return current branch name or exit."""
    try:
        return scrape('git rev-parse --abbrev-ref HEAD')
    except CPE:
        click.echo('There are no commits yet in this repository.')
        sys.exit(0)


def usual_upstream():
    branches = scrape('git for-each-ref --format="%(refname:short)" refs/heads').split('\n')
    upstreams = Counter()
    for branch in branches:
        try:
            # upstream/branch/blablabla
            upstream, branch = scrape('git rev-parse --abbrev-ref %s@{upstream}' % branch).split('/', maxsplit=1)
        except (CPE, ValueError):
            # no upstream for this branch
            continue
        upstreams[upstream] += 1
    try:
        usual_upstream, count = upstreams.most_common(1)[0]
        click.echo('Pushing to your usual remote: ' + click.style(usual_upstream, fg='yellow'))
        return usual_upstream
    except IndexError:
        pass
    # okay, no remote tracking branches yet, lets see if there are actually any upstreams
    try:
        upstream = scrape('git remote').strip().split('\n')[0]
        if upstream:
            return upstream
    except IndexError:
        pass
    # okay, no remotes yet, let's configure one
    click.echo('I couldn\'t find an upstream to push to.')
    upstream = click.prompt('GitHub username, upstream URL (or C-D to abort)').strip()
    if '/' not in upstream:
        # that's an username!
        upstream = 'git@github.com:' + upstream + '/' + repo_name()
    run('git remote add origin ' + upstream)
    click.echo('Created remote ' + click.style('origin', fg='yellow') + ' pointing to ' + click.style(upstream, fg='yellow'))
    return 'origin'


@click.group()
def shit():
    pass


@shit.command()
def gui():
    run('git gui')



@shit.command()
def head():
    """
    Show information about current working tree.
    """
    branch = current_branch()
    upstream = current_upstream()
    click.echo('Branch: ' + click.style(branch, fg='yellow'), nl=not upstream)
    if upstream:
        click.echo(' pushes to ' + click.style(upstream, fg='yellow'))
    dirty = scrape('git diff --shortstat')
    if dirty:
        click.echo('dirty:  ' + dirty)
    staged = scrape('git diff --shortstat --staged')
    if staged:
        click.echo('staged: ' + staged)
    if branch == 'master':
        rev_range = '-1'
    else:
        rev_range = 'master..HEAD'
        click.echo('Commits on this feature branch:')
    run('git log --format="format:%aN: %s" ' + rev_range)


@shit.command()
@click.option('--sign/--no-sign', default=True, help='GPG sign commits (enabled iff key is configured)')
@click.option('--amend/--no-amend', default=False, help='Amend to previous commit')
def commit(sign, amend):
    pass


@shit.command()
@click.argument('branch', required=False)
def checkout(branch='-'):
    """
    Checkout a branch.

    If no branch is given, checkout the previous branch.
    """
    run('git checkout ' + branch)


@shit.command()
@click.argument('branch')
def branch(branch):
    """
    Create a new branch from the current commit.
    """
    run('git checkout -b ' + branch)


@shit.command()
@click.argument('remote', required=False)
def push(remote=''):
    """
    Push changes to a remote repository.

    If no remote is specified, the default remote is used.

    If this is the first push for this branch, then the most commonly
    used remote is used and saved as thed default.
    """
    branch = current_branch()
    upstream = current_upstream()
    if not upstream:
        upstream = usual_upstream()
    run('git push -u ' + upstream + ' ' + branch)


def einscheißen():
    try:
        shit()
    except CPE as cpe:
        click.echo(click.style(' '.join(cpe.cmd), fg='yellow') +
                   ': exited with code ' + click.style(str(cpe.returncode), fg='red', bold=True))

if __name__ == '__main__':
    einscheißen()

