import subprocess

def get_changed_files(base_ref="origin/main"):
    # ใช้ git diff เพื่อหาว่าไฟล์ไหนเปลี่ยน
    result = subprocess.run(
        ["git", "diff", "--name-only", base_ref],
        capture_output=True, text=True
    )
    files = result.stdout.splitlines()
    return files

def filter_workflow_files(files):
    return [f for f in files if f.startswith(".github/workflows/") and f.endswith((".yml", ".yaml"))]

if __name__ == "__main__":
    changed = get_changed_files()
    workflows = filter_workflow_files(changed)
    print("Changed workflow files:", workflows)
