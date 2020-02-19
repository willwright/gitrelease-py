import re


def parse_jira_key(branch):
    reg_ex = re.search("\/([A-Z])+-\d+", branch)
    jira_key = reg_ex.group().replace("/", "", 1)
    return jira_key