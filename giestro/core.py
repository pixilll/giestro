# giestro/core.py

import os, shutil, sys, subprocess
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

class Giestro:
    GIEST_DIR = ".giest"

    def __init__(self):
        self.repo_path = os.getcwd()
        self.giest_dir = os.path.join(self.repo_path, self.GIEST_DIR)
        self.branches_dir = os.path.join(self.giest_dir, "branches")
        self.console = Console()

    def init(self):
        if not os.path.exists(self.giest_dir):
            self.console.print(Panel("giestro initialized"))
            os.makedirs(self.branches_dir)
            self.branch("main")
        else:
            self.console.print(Panel("giestro already initialized"))

    def commit(self, branch, message):
        try:
            commit_id = f"commit-{len(os.listdir(os.path.join(self.branches_dir, branch))) + 1}"
        except FileNotFoundError:
            self.console.print(Panel(f"branch {branch} does not exist.", style="red"))
            return
        commit_path = os.path.join(self.branches_dir, branch, commit_id)
        os.makedirs(commit_path)

        for item in os.listdir(self.repo_path):
            if item in [".giest", "MERGE.giest"]:
                continue
            item_path = os.path.join(self.repo_path, item)
            if item != self.GIEST_DIR:
                if os.path.isfile(item_path):
                    shutil.copy2(item_path, commit_path)
                elif os.path.isdir(item_path):
                    shutil.copytree(item_path, os.path.join(commit_path, item))

        commit_message_path = os.path.join(commit_path, "message.txt")
        with open(commit_message_path, "w") as f:
            f.write(message)

        self.console.print(Panel(f"committed as {commit_id} with message: '{message}'\nrun giestro fetch {branch} {commit_id} to rollback to this point."))

    def history(self, branch):
        try:
            commits = os.listdir(os.path.join(self.branches_dir, branch))
        except FileNotFoundError:
            self.console.print(Panel(f"branch {branch} does not exist.", style="red"))
            return
        if not commits:
            self.console.print(Panel("no commits yet"))
            return

        history_output = "\n".join(
            [
                f"{commit} - {datetime.fromtimestamp(os.path.getctime(os.path.join(self.branches_dir, branch, commit)))}\n  message: {self._get_commit_message(branch, commit) or 'no message provided'}"
                for commit in commits
            ]
        )
        self.console.print(Panel(history_output))

    def _get_commit_message(self, branch, commit):
        commit_message_path = os.path.join(self.branches_dir, branch, commit, "message.txt")
        if os.path.exists(commit_message_path):
            with open(commit_message_path) as f:
                return f.read().strip()
        return "(no message)"

    def merge_request(self, source, target, message):
        source_path = os.path.join(self.branches_dir, source)
        merge_path = os.path.join(source_path, "MERGE.giest")
        target_path = os.path.join(self.branches_dir, target)
        if not os.path.exists(source_path):
            self.console.print(Panel(f"branch {source} does not exist.", style="red"))
            return
        if not os.path.exists(target_path):
            self.console.print(Panel(f"branch {target} does not exist.", style="red"))
            return

        with open(merge_path, "w") as file:
            file.write(message)

        self.console.print(Panel(f"merge request created from {source} to {target} with message: {message}.", style="green"))

    def rollback(self, branch, commit_id):
        commit_path = os.path.join(self.branches_dir, branch, commit_id)
        if not os.path.exists(os.path.join(self.branches_dir, branch)):
            self.console.print(Panel(f"branch {branch} does not exist.", style="red"))
            return
        if not os.path.exists(commit_path):
            self.console.print(Panel(f"commit {commit_id} not found", style="red"))
            return

        for item in os.listdir(self.repo_path):
            item_path = os.path.join(self.repo_path, item)
            if item != self.GIEST_DIR:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

        for item in os.listdir(commit_path):
            if item in [".giest", "MERGE.giest"]:
                continue
            item_path = os.path.join(commit_path, item)
            if os.path.isfile(item_path):
                shutil.copy2(item_path, self.repo_path)
            elif os.path.isdir(item_path):
                shutil.copytree(item_path, os.path.join(self.repo_path, item))

        self.console.print(Panel(f"rolled back to {commit_id} from branch {branch}"))

    def remove(self, branch, commit_id):
        commit_path = os.path.join(self.branches_dir, branch, commit_id)
        if not os.path.exists(os.path.join(self.branches_dir, branch)):
            self.console.print(Panel(f"branch {branch} does not exist.", style="red"))
            return
        if not os.path.exists(commit_path):
            self.console.print(Panel(f"commit {commit_id} not found", style="red"))
            return

        shutil.rmtree(commit_path)
        self.console.print(Panel(f"removed {commit_id} on branch {branch}"))

    def branch(self, branch_name):
        branch_path = os.path.join(self.branches_dir, branch_name)
        if os.path.exists(branch_path):
            self.console.print(Panel(f"branch {branch_name} already exists", style="red"))
            return

        os.makedirs(branch_path)

        self.console.print(Panel(f"branch {branch_name} created"))

    def list_branches(self):
        self.console.print(Panel("available branches:\n"+("\n".join([('- '+i) for i in os.listdir(self.branches_dir)]))))

    def merge(self, source, target):
        source_path = os.path.join(self.branches_dir, source)
        merge_path = os.path.join(source_path, "MERGE.giest")
        target_path = os.path.join(self.branches_dir, target)
        if not os.path.exists(source_path):
            self.console.print(Panel(f"branch {source} does not exist.", style="red"))
            return
        if not os.path.exists(target_path):
            self.console.print(Panel(f"branch {target} does not exist.", style="red"))
            return
        if os.path.exists(merge_path):
            with open(merge_path) as file:
                content = file.read().strip()
                if content:
                    self.console.print(Panel(f"\n{content}\n", title="a merge request exists for this merge operation:", title_align="left"))
        merged = 0
        run = True
        for item in os.listdir(source_path):
            if item in [".giest", "MERGE.giest"]:
                continue
            if item in os.listdir(target_path):
                self.console.print(Panel(f"conflicting commit: {item}\ntype 'y' to overwrite {target}/{item} with {source}/{item}, type 'n' to avoid merging this commit.", style="yellow"))
                while True:
                    match input("y/n: ").lower():
                        case "y":
                            break
                        case "n":
                            run = False
                            break
            if run:
                if os.path.exists(os.path.join(target_path, item)):
                    shutil.rmtree(os.path.join(target_path, item))
                shutil.copytree(os.path.join(source_path, item), os.path.join(target_path, item))
                merged += 1
        self.console.print(Panel(f"merged {merged} commit{'s' if merged != 1 else ''}", style=("green" if merged else "white")))

    def remove_branch(self, branch):
        try:
            shutil.rmtree(os.path.join(self.branches_dir, branch))
        except FileNotFoundError:
            self.console.print(Panel(f"branch {branch} does not exist.", style="red"))
            return
        self.console.print(Panel(f"branch {branch} removed"))
    def fetch(self, url: str):
        fetch_snapshot = os.path.join(os.path.dirname(__file__), "FETCH_SNAPSHOT")
        url = f"https://github.com/{url.removeprefix("gh:")}.git" if url.startswith("gh:") else url
        self.console.print(Panel("fetching is irreversible (unless you have a commit saved before it was done).\nit is recommended to commit before fetching to preserve a backup of your workspace.\npress return to continue, or ctrl-c to abort.", title="warning", title_align="left", style="yellow"))
        input()
        self.console.print(Panel(f"fetching from git repo at {url}..."))
        shutil.copytree(self.repo_path, fetch_snapshot)
        for item in os.listdir(self.repo_path):
            item_path = os.path.join(self.repo_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        self.console.print(Panel(f"cleared project directory and created fetch snapshot in preparation for git repository cloning"))
        self.console.print(Panel("\n" + subprocess.run(
            ["git", "clone", url, self.repo_path],
            text=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        ).stdout.lower(), style="blue", title="git output", title_align="left"))
        self.console.print(Panel(f"git repository cloned, reintegrating .giest and MERGE.giest (if present) from {fetch_snapshot}"))
        for item in [".giest", "MERGE.giest"]:
            item_path = os.path.join(fetch_snapshot, item)
            if os.path.isfile(item_path):
                shutil.copy2(item_path, os.path.join(self.repo_path, item))
            elif os.path.isdir(item_path):
                shutil.copytree(item_path, os.path.join(self.repo_path, item))
        self.console.print(Panel(f"deleting {fetch_snapshot}..."))
        shutil.rmtree(fetch_snapshot)
        self.console.print(Panel(f"fetch was successful.", style="green"))

    def ensure_init(self):
        if not os.path.exists(self.giest_dir):
            self.console.print(Panel("not a giest. run giestro init to initialize one here", style="red"))
            exit(1)

def main():
    giestro: Giestro = Giestro()
    if len(sys.argv) < 2:
        giestro.console.print(Panel("please provide a command, or run giestro help to see a list of commands.", style="red"))
    else:
        command = sys.argv[1].lower()
        try:
            if command not in ["init", "help"]:
                giestro.ensure_init()
            match command:
                case "init":
                    giestro.init()
                case "commit":
                    giestro.commit(sys.argv[2], " ".join(sys.argv[3:]))
                case "history":
                    giestro.history(sys.argv[2])
                case "get":
                    giestro.rollback(sys.argv[2], sys.argv[3])
                case "remove-commit":
                    giestro.remove(sys.argv[2], sys.argv[3])
                case "branch":
                    giestro.branch(sys.argv[2])
                case "branches":
                    giestro.list_branches()
                case "remove-branch":
                    giestro.remove_branch(sys.argv[2])
                case "merge":
                    giestro.merge(sys.argv[2], sys.argv[3])
                case "merge-request":
                    giestro.merge_request(sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]))
                case "fetch":
                    giestro.fetch(sys.argv[2])
                case "help":
                    print(f"commands: init, commit, history, get, remove-commit, branch, branches, remove-branch, merge, create-issues, list-issues, merge-request, fetch, help")
                case _:
                    giestro.console.print(Panel(f"unknown command: {command}", style="red"))
        except IndexError:
            giestro.console.print(Panel(f"not enough arguments supplied for giestro {command}", style="red"))
        except KeyboardInterrupt:
            exit()
        except Exception as err:
            giestro.console.print(Panel(str(err).lower(), title="internal error", title_align="left", style="red"))