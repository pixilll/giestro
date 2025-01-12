# giestro/core.py

import os
import shutil
import sys
from datetime import datetime

class Giestro:
    GIEST_DIR = ".giest"

    def __init__(self):
        self.repo_path = os.getcwd()
        self.giest_dir = os.path.join(self.repo_path, self.GIEST_DIR)
        self.bin_dir = os.path.join(self.giest_dir, "bin")

    def init(self):
        if not os.path.exists(self.giest_dir):
            os.makedirs(self.bin_dir)
            print("giestro initialized")
        else:
            print("giestro already initialized")

    def commit(self):
        if not os.path.exists(self.giest_dir):
            print("not a giest repo. run 'giestro init'")
            return

        commit_id = f"commit-{len(os.listdir(self.bin_dir)) + 1}"
        commit_path = os.path.join(self.bin_dir, commit_id)
        os.makedirs(commit_path)

        for item in os.listdir(self.repo_path):
            item_path = os.path.join(self.repo_path, item)
            if item != self.GIEST_DIR:
                if os.path.isfile(item_path):
                    shutil.copy2(item_path, commit_path)
                elif os.path.isdir(item_path):
                    shutil.copytree(item_path, os.path.join(commit_path, item))

        print(f"committed as {commit_id}")

    def history(self):
        if not os.path.exists(self.giest_dir):
            print("not a giest repo. run 'giestro init'")
            return

        commits = os.listdir(self.bin_dir)
        if not commits:
            print("no commits yet")
            return

        for commit in commits:
            commit_path = os.path.join(self.bin_dir, commit)
            timestamp = datetime.fromtimestamp(os.path.getctime(commit_path))
            print(f"{commit} - {timestamp}")

    def rollback(self, commit_id):
        if not os.path.exists(self.giest_dir):
            print("not a giest repo. run 'giestro init'")
            return

        commit_path = os.path.join(self.bin_dir, commit_id)
        if not os.path.exists(commit_path):
            print(f"commit {commit_id} not found")
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

        print(f"rolled back to {commit_id}")

if __name__ == "__main__":
    giestro = Giestro()
    if len(sys.argv) < 2:
        print("usage: giestro <command> [args]")
    else:
        command = sys.argv[1].lower()
        if command == "init":
            giestro.init()
        elif command == "commit":
            giestro.commit()
        elif command == "history":
            giestro.history()
        elif command == "rollback":
            if len(sys.argv) < 3:
                print("usage: giestro rollback <commit-id>")
            else:
                giestro.rollback(sys.argv[2])
        else:
            print("unknown command")