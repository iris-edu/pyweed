import requests
from pypandoc import convert_text
import logging
from tempfile import NamedTemporaryFile
from future.moves.subprocess import check_output
from future.moves.configparser import ConfigParser
import os.path
import re
from time import sleep


class GitHubClient(object):
    BASE_URL = 'https://api.github.com'
    BASE_HEADERS = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "iris-edu/pyweed/repo-importer",
        }

    def __init__(self, owner="example", project="example", token="example"):
        self.headers = self.BASE_HEADERS.copy()
        self.headers['Authorization'] = 'Basic %s' % token

        self.issues_url = '%s/repos/%s/%s/issues' % (self.BASE_URL, owner, project)

    def list(self):
        """
        List all issues
        """
        issues = []
        page = 1
        while True:
            print("Getting page %d of GitHub issues" % page)
            r = requests.get(
                self.issues_url,
                params={'page': page, 'state': 'all'},
                headers=self.headers,
            )
            r.raise_for_status()
            json_data = r.json()
            if len(json_data):
                issues.extend(json_data)
                page += 1
            else:
                break
        return issues

    def close(self, issue_number):
        """
        Close an issue
        """
        edit_issue_url = "%s/%s" % (self.issues_url, issue_number)
        r = requests.patch(
            edit_issue_url,
            json={
                "state": "closed",
            },
            headers=self.headers,
        )
        r.raise_for_status()

    def create(self, issue_json):
        """
        Create an issue
        """
        # Limit the rate of creation
        # see https://developer.github.com/guides/best-practices-for-integrators/#dealing-with-abuse-rate-limits
        sleep(1)
        r = requests.post(
            self.issues_url,
            json=issue_json,
            headers=self.headers,
        )
        r.raise_for_status()
        return r.json()['number']


class RedmineClient(object):
    BASE_URL = 'http://dmscode.iris.washington.edu'

    def __init__(self, project="example", redmine_key="example"):
        self.redmine_key = redmine_key
        self.issues_url = "%s/projects/%s/issues.json" % (self.BASE_URL, project)

    def list(self):
        """
        List all issues
        """
        issues = []
        offset = 0
        limit = 50
        total = -1
        while (total < 0) or (total > offset):
            print("Loading %d issues from Redmine" % limit)
            r = requests.get(
                self.issues_url,
                json = {
                    'status_id': '*',
                    'key': self.redmine_key,
                    'offset': offset,
                    'limit': limit,
                }
            )
            r.raise_for_status()
            json_data = r.json()
            issues.extend(json_data['issues'])
            offset += limit
            total = json_data['total_count']
        return issues


class RedmineToGitHub(object):

    def __init__(self, redmine_client=None, github_client=None):
        self.redmine_client = redmine_client or RedmineClient()
        self.github_client = github_client or GitHubClient()
        self.issue_mapping = {}
        self.closed_github_issues = set()

    def is_closed(self, redmine_issue):
        return 'closed_on' in redmine_issue

    def convert_issue(self, redmine_issue):
        """
        Turn a Redmine issue into a GitHub issue
        """
        redmine_issue_id = str(redmine_issue['id'])
        github_issue_id = self.issue_mapping.get(redmine_issue_id)
        if github_issue_id:
            print("Redmine #%s is already in GitHub as #%s" % (redmine_issue_id, github_issue_id))
        else:
            print("Converting Redmine #%s (%s)" % (redmine_issue_id, redmine_issue['subject']))
            github_issue_id = str(self.github_client.create(self.convert_issue_data(redmine_issue)))
            print("Created GitHub #%s" % github_issue_id)
            self.issue_mapping[redmine_issue_id] = github_issue_id

        # Close the issue if appropriate
        if self.is_closed(redmine_issue) and github_issue_id not in self.closed_github_issues:
            print("Marking #%s as closed" % github_issue_id)
            self.github_client.close(github_issue_id)
        return github_issue_id

    def convert_issue_data(self, redmine_issue):
        """
        Generate the data for a new GitHub issue
        """
        description_md = convert_text(
            redmine_issue['description'], 'markdown_github', 'textile'
        )
        porting_note = '###### ported from Redmine #%s (created %s)' % (
            redmine_issue['id'],
            redmine_issue['created_on'].split('T')[0]
        )
        if self.is_closed(redmine_issue):
            porting_note = '%s (CLOSED %s)' % (
                porting_note,
                redmine_issue['closed_on'].split('T')[0]
            )
        body = "%s\n\n%s" % (porting_note, description_md)
        title = "%(subject)s (RM#%(id)s)" % redmine_issue
        return {
            "title": title,
            "body": body,
            "assignees": ["adam-iris"],
        }

    def get_existing_mapping(self):
        self.issue_mapping = {}
        self.closed_github_issues.clear()
        print("Looking for existing GitHub issues")
        for github_issue in self.github_client.list():
            m = re.search(r'RM#(\d+)', github_issue['title'])
            if m:
                github_issue_id = str(github_issue['number'])
                self.issue_mapping[m.group(1)] = github_issue_id
                if github_issue['state'] == 'closed':
                    self.closed_github_issues.add(github_issue_id)

    def convert_issues(self):
        self.get_existing_mapping()
        print("Reading Redmine issues")
        for redmine_issue in self.redmine_client.list():
            self.convert_issue(redmine_issue)

    def setup_git_update(self):
        """
        Generate a filter to run on the git repo, eg.

        git filter-branch --msg-filter {{ filter }} HEAD
        """
        with NamedTemporaryFile('w+t', delete=False) as f:
            f.write(FILTER_TEMPLATE % str(self.issue_mapping))
        cmd = "git filter-branch -f --msg-filter 'python %s' -- --all" % f.name
        print("To update the Git repository, run\n%s" % cmd)

FILTER_TEMPLATE = """
#! python

import re
import sys

MAPPINGS = %s

def subfn(m):
    '''
    Function to call with re.sub(), takes a re.match object with a Redmine issue number
    and returns the corresponding GitHub issue number
    '''
    return MAPPINGS.get(m.group(0), m.group(0))

for line in sys.stdin:
    print(re.sub(r'(?<=#)\\d+\\b', subfn, line))
""".strip()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    config = ConfigParser()
    config.read_dict({
        'GITHUB': {
            'org': 'iris-edu',
            'repo': 'pyweed',
            'token': 'example',
        },
        'REDMINE': {
            'project': 'pyweed',
            'key': 'example',
        },
    })
    config_file = os.path.expanduser("~/.redmine_to_git.cfg")
    if os.path.exists(config_file):
        config.read([config_file])
    else:
        with open(config_file, 'w+t') as f:
            config.write(f)
        print("Please update %s to include GitHub auth token and Redmine auth key" % config_file)
        exit(1)
    redmine_client = RedmineClient(config.get('REDMINE', 'project'), config.get('REDMINE', 'key'))
    github_client = GitHubClient(config.get('GITHUB', 'org'), config.get('GITHUB', 'repo'), config.get('GITHUB', 'token'))
    rtg = RedmineToGitHub(redmine_client, github_client)

    rtg.convert_issues()
    rtg.setup_git_update()





