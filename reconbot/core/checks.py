import shutil
import sys

if shutil.which("nmap") is None:
    print("[+]Bilgisayarınızda nmap kurulu değil tool başlatılamadı!")
    sys.exit(1)
        
    
if shutil.which("gobuster") is None:
    print("[+]Bilgisayarınızda gobuster kurulu değil tool başlatılamadı!")
    sys.exit(1)
    
if shutil.which("nuclei") is None:
    print("[+]Bilgisayarınızda nuclei kurulu değil tool başlatılamadı!")
    sys.exit(1)