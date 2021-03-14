import subprocess
import os

def get_branches(path):
    branches = subprocess.check_output(["git", "branch"], cwd=path).decode("utf-8").split("\n")[0:-1]
    current = ""
    result = []
    for branch in branches:
        if branch[0] == "*":
            current = branch
        result.append(branch[2:])
    return result, current

def checkout_branch(path, branch):
    return subprocess.check_call(["git", "checkout", branch], cwd=path)

def get_games():
    result = []
    for filename in os.listdir("/home/cpi/games"):
        filename = os.path.join("/home/cpi/games", filename)
        if os.path.isdir(filename) and is_git(filename):
            result.append(filename)
    return result

def is_git(path):
    return os.path.join(path, ".git")