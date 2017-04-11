import requests
from pypandoc import convert_text
from logging import getLogger

LOGGER = getLogger(__name__)


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
        r = requests.get(
            self.issues_url,
            headers=self.headers,
        )
        r.raise_for_status()
        return r.json()

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
        r = requests.get(
            self.issues_url,
            json = {
                'status_id': '*',
                'limit': 2,
                'key': self.redmine_key,
            }
        )
        r.raise_for_status()
        return r.json()['issues']


class RedmineToGitHub(object):

    def __init__(self, redmine_client=None, github_client=None):
        self.redmine_client = redmine_client or RedmineClient()
        self.github_client = github_client or GitHubClient()
        self.issue_mapping = {}

    def is_closed(self, redmine_issue):
        return 'closed_on' in redmine_issue

    def convert_issue(self, redmine_issue):
        issue_id = self.github_client.create(self.convert_issue_data(redmine_issue))
        LOGGER.info("Created GitHub #%s from Redmine %s (%s)" % (
            issue_id,
            redmine_issue['id'],
            redmine_issue['subject']
        ))
        self.issue_mapping[redmine_issue['id']] = issue_id
        if self.is_closed(redmine_issue):
            self.github_client.close(issue_id)
        LOGGER.info("Closed #%s" % issue_id)
        return issue_id

    def convert_issue_data(self, redmine_issue):
        redmine_issue['author_name'] = redmine_issue['author']['name']
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

    def to_github(self):
        for redmine_issue in self.redmine_client.list():
            self.convert_issue(redmine_issue)
        return self.issue_mapping

    def git_filter(self):
        """
        Generate a filter to run on the git repo, eg.

        git filter-branch -f --tree-filter {{ filter }} HEAD
        """
        pass

