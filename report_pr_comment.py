from github import Github
import os
import json

def read_json(filepath):
    """
    Read a json file as a dictionary.
    Parameters
    ----------
    filepath : str
    Returns
    -------
    data : dict
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def get_actions_input(input_name):
    """
    Get a Github actions input by name.
    Parameters
    ----------
    input_name : str
    Returns
    -------
    action_input : str
    Notes
    -----
    GitHub Actions creates an environment variable for the input with the name:
    INPUT_<CAPITALIZED_VARIABLE_NAME> (e.g. "INPUT_FOO" for "foo")
    References
    ----------
    .. [1] https://help.github.com/en/actions/automating-your-workflow-with-github-actions/metadata-syntax-for-github-actions#example  # noqa: E501
    """
    return os.getenv('INPUT_{}'.format(input_name).upper())


def load_template(filename):
    """
    Load a template.
    Parameters
    ----------
    filename : template file name
    Returns
    -------
    template : str
    """
    template_path = os.path.join('.github/workflows', filename)
    with open(template_path, 'r') as f:
        return f.read()

def report():
    # search a pull request that triggered this action
    gh = Github(os.getenv('GITHUB_TOKEN'))
    event = read_json(os.getenv('GITHUB_EVENT_PATH'))
    branch_label = event['pull_request']['head']['label']  # author:branch
    branch_name = branch_label.split(':')[-1]
    repo = gh.get_repo(event['repository']['full_name'])
    prs = repo.get_pulls(state='open', sort='created', head=branch_label)
    pr = prs[0]

    # load template
    #template = load_template(get_actions_input('filename'))
    template = load_template('template.md')

    # build a comment
    pr_info = {
        'pull_id': pr.number,
        'branch_name': branch_name
    }
    new_comment = template.format(**pr_info)

    # check if this pull request has a duplicated comment
    old_comments = [c.body for c in pr.get_issue_comments()]
    if new_comment in old_comments:
        print('This pull request already a duplicated comment.')
        exit(0)

    # add the comment
    pr.create_issue_comment(new_comment)

if __name__ == '__main__':
    report()

