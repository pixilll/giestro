# giestro/core.py

import os
import shutil
import sys
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

    def commit(self, branch):
        if not os.path.exists(self.giest_dir):
            self.console.print(Panel("not a giest. run giestro init to initialize one here", style="red"))
            return
        try:
            commit_id = f"commit-{len(os.listdir(os.path.join(self.branches_dir, branch))) + 1}"
        except FileNotFoundError:
            self.console.print(Panel(f"branch {branch} does not exist.", style="red"))
            return
        commit_path = os.path.join(self.branches_dir, branch, commit_id)
        os.makedirs(commit_path)

        for item in os.listdir(self.repo_path):
            item_path = os.path.join(self.repo_path, item)
            if item != self.GIEST_DIR:
                if os.path.isfile(item_path):
                    shutil.copy2(item_path, commit_path)
                elif os.path.isdir(item_path):
                    shutil.copytree(item_path, os.path.join(commit_path, item))

        self.console.print(Panel(f"committed as {commit_id}\nrun giestro fetch {branch} {commit_id} to rollback to this point."))

    def history(self, branch):
        if not os.path.exists(self.giest_dir):
            self.console.print(Panel("not a giest. run giestro init to initialize one here", style="red"))
            return
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
                f"{commit} - {datetime.fromtimestamp(os.path.getctime(os.path.join(self.branches_dir, branch, commit)))}"
                for commit in commits
            ]
        )
        self.console.print(Panel(history_output))

    def rollback(self, branch, commit_id):
        if not os.path.exists(self.giest_dir):
            self.console.print(Panel("not a giest. run giestro init to initialize one here", style="red"))
            return

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
            item_path = os.path.join(commit_path, item)
            if os.path.isfile(item_path):
                shutil.copy2(item_path, self.repo_path)
            elif os.path.isdir(item_path):
                shutil.copytree(item_path, os.path.join(self.repo_path, item))

        self.console.print(Panel(f"rolled back to {commit_id} from branch {branch}"))

    def remove(self, branch, commit_id):
        if not os.path.exists(self.giest_dir):
            self.console.print(Panel("not a giest. run giestro init to initialize one here", style="red"))
            return

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
        target_path = os.path.join(self.branches_dir, target)
        if not os.path.exists(source_path):
            self.console.print(Panel(f"branch {source_branch} does not exist.", style="red"))
            return
        if not os.path.exists(target_path):
            self.console.print(Panel(f"branch {target_branch} does not exist.", style="red"))
            return
        merged = 0
        run = True
        for item in os.listdir(source_path):
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

def main():
    giestro = Giestro()
    if len(sys.argv) < 2:
        giestro.console.print(Panel("usage: giestro <command> [args]", style="red"))
    else:
        command = sys.argv[1].lower()
        try:
            match command:
                case "init":
                    giestro.init()
                case "commit":
                    giestro.commit(sys.argv[2])
                case "history":
                    giestro.history(sys.argv[2])
                case "fetch":
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
                case "help":
                    print(f"commands: init, commit, history, fetch, remove-commit, branch, branches, remove-branch, merge, help")
                case _:
                    giestro.console.print(Panel("unknown command", style="red"))
        except IndexError:
            giestro.console.print(Panel(f"not enough arguments supplied for giestro {command}", style="red"))