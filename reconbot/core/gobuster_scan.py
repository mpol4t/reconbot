import subprocess
from urllib.parse import urljoin

allowed_status = {200,301,302,401,403}
def run_gobuster(url, wordlist):
    p1 = subprocess.run(
        ["gobuster", "dir", "-u", url, "-w", wordlist],
        capture_output=True,
        text=True
    )
    if p1.returncode != 0:
        return []
    results = []
    for line in p1.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if '(' not in line or 'Status:' not in line:
            continue
        left , right = line.split('(', 1)
        path = left.strip()
        
        status_part = right.replace(')','').strip()
        if not status_part.startswith('Status'):
            continue
        status_str = status_part.split(':',1)[1].strip()
        status_str = status_str.split()[0]
        if not status_str.isdigit():
            continue
        status_int = int(status_str)
        if status_int not in allowed_status:
            continue
        
        results.append({
            'path': path,
            'status': status_int,
            'url': urljoin(url,path)
            })
        
    return results