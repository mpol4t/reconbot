import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET 
from datetime import datetime
import tempfile
import os 
import sys

def run_nmap(ip: str) -> tuple[str, Path]:
    fd, xml_path = tempfile.mkstemp(suffix=".xml")
    os.close(fd)
    print("[+] Nmap başlatılıyor...")
    result = subprocess.run(
        ["nmap",'-sV', "--top-ports", "1000", "-T4", "-oX", xml_path ,ip],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    else:
        print(result.stdout)
        return result.stdout, Path(xml_path)


def parse_nmap_xml(xml_path, ip):
    urls = []
    if not xml_path.exists():
        print("Parse edilecek XML dosyası bulunamadı!!!")
        return []
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    common_web_ports = {"80", "443", "8080", "8000", "8443", "3000", "5000"}
    for port in root.iter("port"):
        port_numarası = port.attrib["portid"]
        state_element = port.find("state")
        if state_element is None:
            continue
        state = state_element.attrib["state"]
        service_element = port.find("service")
        if service_element is None:
            continue
        servis = service_element.attrib.get("name", "")
        servis = servis.lower()

        if state != "open":
            continue

        is_http_service = "http" in servis
        is_common_web_port = port_numarası in common_web_ports

        if not (is_http_service or is_common_web_port):
            continue

        if "https" in servis or port_numarası in {"443", "8443"}:
            scheme = "https"
        else:
            scheme = "http"

        urls.append(f"{scheme}://{ip}:{port_numarası}")
    
    return urls
            


def detailed_nmap(ip: str) -> subprocess.Popen:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    desktop_path = Path.home() / "Desktop" / f"detailed_nmap_{ts}.txt"
    desktop_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[+] Detailed nmap arka planda başlatıldı {desktop_path}")
    
    with open(desktop_path, 'w') as file:
        proc = subprocess.Popen(
            ["nmap", "-Pn", "-p-", "-sV", "-v", "-T4", "--stats-every", "5s", ip],
            start_new_session=True,
            stdout=file,
            stderr=file
        )

    print(f"[+] Detailed nmap PID: {proc.pid}")
    return proc