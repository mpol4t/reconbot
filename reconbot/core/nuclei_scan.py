import subprocess
from pathlib import Path
import os
import tempfile
import json

def start_nuclei(targets: list[str]) -> tuple[subprocess.Popen, Path]:
    Findings = []
    parse_error_count = 0
    print("Targets", targets)
    if not targets:
        
        return {
            "Status": "No_targets",
            "Error": None,
            "Findings": [],
        }
        
    tmpdir = tempfile.mkdtemp()
    targets_path = Path(tmpdir) / "targets.txt"
    with targets_path.open("w") as f:
        f.write("\n".join(targets) + "\n")

    output_path = Path(tmpdir) / "output.jsonl"
    nuclei_proc = subprocess.Popen(
        ["nuclei", "-l", str(targets_path), "-jsonl", "-o", str(output_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )
    print(f"[+] Nuclei started with PID: {nuclei_proc.pid}")
    return nuclei_proc, output_path

def parse_nuclei_output(output_path: Path, returncode: int, stderr_data: str) -> dict:
    Findings = []
    parse_error_count = 0
    seen = set()

    if not output_path.exists():
        return {
            "Status": "Error",
            "Error": stderr_data,
            "Findings": []
        }

    if output_path.stat().st_size == 0:
        return {
            "Status": "Clean",
            "Error": None,
            "Findings": []
        }

    with output_path.open("r") as f:
        for line in f:
            try:
                data = json.loads(line)
                template = data.get("templateID") or data.get("template-id")
                host = data.get("host")
                matched_at = data.get("matched-at") or data.get("matchedAt") or host
                key = f"{matched_at}:{template}"

                if key in seen:
                    continue
                seen.add(key)

                Findings.append(data)

            except json.JSONDecodeError:
                parse_error_count += 1
                continue

    if returncode != 0 and not Findings:
        return {
            "Status": "Error",
            "Error": stderr_data,
            "Findings": []
        }

    if returncode != 0 or parse_error_count > 0:
        return {
            "Status": "Partial",
            "Error": stderr_data,
            "Findings": Findings
        }

    return {
        "Status": "Success",
        "Error": None,
        "Findings": Findings
    }