import os
from pathlib import Path
import subprocess


code = Path(__file__).parent.parent / "code"

for path in sorted(code.rglob("*.py")):
    cmd = ["python", path]
    filename = os.path.basename(path).split(".")[0] + "_out.txt"
    result = subprocess.run(cmd, capture_output=True, text=True)
    with open(os.path.join(code, "out", filename), "w") as f:
        f.write(result.stdout)
