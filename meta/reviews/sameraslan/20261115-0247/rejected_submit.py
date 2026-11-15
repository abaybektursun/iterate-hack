"""Records that `tools/gpu.py submit` leaves in the jobs Dict when Modal rejects the spawn, and when it accepts it.
Run from the repository root (no Modal call: modal is replaced by a fake whose Dict is a dict):

  python3 meta/reviews/sameraslan/20261115-0247/rejected_submit.py

The last line counts the real records: rows of `gpu.py ls --all` in state "submitting" (read only).
"""
import subprocess
import sys
import types


class Volume:
    def batch_upload(self, force):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *error):
        return False

    def put_file(self, data, path):
        pass


class Function:
    reject = True

    def spawn(self, job_id):
        if Function.reject:
            raise RuntimeError("workspace billing cycle spend limit reached")
        return types.SimpleNamespace(object_id="fc-fake")


store = {}
modal = types.ModuleType("modal")
modal.Dict = types.SimpleNamespace(from_name=lambda *a, **k: store)
modal.Volume = types.SimpleNamespace(from_name=lambda *a, **k: Volume())
modal.Function = types.SimpleNamespace(from_name=lambda *a, **k: Function())
sys.modules["modal"] = modal
sys.path.insert(0, "tools")
import gpu  # noqa: E402

real_git = gpu.git  # submit asserts a clean, pushed tree; the review's own edits make it dirty
gpu.git = lambda *args: "" if args[0] == "status" else "origin/fake" if args[0] == "branch" else real_git(*args)

for reject in (True, False):
    Function.reject = reject
    store.clear()
    try:
        gpu.submit(["cpu", "--", "true"])
        raised = "nothing"
    except RuntimeError as error:
        raised = f"RuntimeError: {error}"
    kinds = sorted(key.split(":")[0] for key in store)
    print(f"spawn {'rejected' if reject else 'accepted'}: submit raised {raised}; records left: {kinds}")

sys.modules.pop("modal")
rows = subprocess.run(["uv", "run", "--quiet", "tools/gpu.py", "ls", "--all"], capture_output=True, text=True, check=True).stdout
print(f"gpu.py ls --all: {sum('  submitting  ' in row for row in rows.splitlines())} rows in state submitting of {len(rows.splitlines())}")
