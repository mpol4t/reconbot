from reconbot.core.nmap_scan import run_nmap, parse_nmap_xml, detailed_nmap
from reconbot.core.gobuster_scan import run_gobuster
from reconbot.core.nuclei_scan import start_nuclei, parse_nuclei_output
from pathlib import Path
import webbrowser
import argparse


def main():
    gobuster_results = {}

    parser = argparse.ArgumentParser(
        description="Reconbot - Automated Nmap + Gobuster reconnaissance tool"
    )
    parser.add_argument(
        "ip",
        help="Target IP address"
    )
    parser.add_argument(
        "-w", "--wordlist",
        required=True,
        help="Path to gobuster wordlist"
    )
    args = parser.parse_args()

    ip = args.ip
    wordlist = args.wordlist
    
    print(f"[+] IP: {ip}")
    print(f"[+] Wordlist: {wordlist}")
    
    detailed_nmap(ip)
    
    try:
        nmap_output , xml_path= run_nmap(ip)
        web_urls = parse_nmap_xml(xml_path, ip)
    except Exception as e:
        print(f"[!] Nmap veya XML parse hatası: {e}")
        print("[!] Program sonlandırılıyor.")
        return 
    
    
    if not web_urls:
        print("[+] Web listesi bulunamadı!")
        print("[+] Detaylı nmap çıktısına bak!")
        print("[+] Program sonlandırılıyor!!")
        return generate_report(gobuster_results, {}, ip, nmap_output)
    
    for x in web_urls:
        print(f"[+] Gobuster başlatılıyor: {x}")
        gobuster_sonuç = run_gobuster(x, wordlist)
        gobuster_results[x] = gobuster_sonuç

    for url, results in gobuster_results.items():
        print(f"==={url}===")
        if not results:
            print("No paths found!")
        else:
            for item in results:
                status = item.get("status")
                path = item.get("path")
                print(f"[{status}] {path}")
            print()

    generate_report(gobuster_results, {}, ip, nmap_output)

    targets = []
    for results in gobuster_results.values():
        for item in results:
            url = item.get("url")
            if url:
                targets.append(url)

    targets = list(set(targets))

    nuclei_proc = None
    nuclei_output_path = None
    nuclei_results = {}


    if targets:
        nuclei_proc, nuclei_output_path = start_nuclei(targets)
        print("[+] Nuclei arka planda başlatıldı...")
    else:
        print("[+] Nuclei için uygun target bulunamadı.")
        return

    if nuclei_proc:
        print("[+] Nuclei tamamlanması bekleniyor...")
        nuclei_proc.wait()

        stderr_data = nuclei_proc.stderr.read() if nuclei_proc.stderr else None

        nuclei_results = parse_nuclei_output(
            nuclei_output_path,
            nuclei_proc.returncode,
            stderr_data
        )

        print("[+] Nuclei tamamlandı, rapor güncelleniyor...")
        generate_report(gobuster_results, nuclei_results, ip, nmap_output)

def generate_report(gobuster_results: dict, nuclei_results: dict, target_ip: str, nmap_output: str):
    report_dir = Path(__file__).resolve().parent
    report_path = report_dir / "report.html"

    html = f"""
    <html>
    <head>
        <title>ReconBot Report</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background:#0e1117; color:#e6edf3; }}
            h1, h2 {{ color:#58a6ff; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 30px; }}
            th, td {{ border: 1px solid #30363d; padding: 8px; text-align:left; }}
            th {{ background-color: #161b22; }}
            tr:nth-child(even) {{ background-color:#161b22; }}
            .status-200 {{ color: #3fb950; font-weight: bold; }}
            .status-403 {{ color: #d29922; font-weight: bold; }}
            .status-404 {{ color: #8b949e; }}
            .status-other {{ color: #58a6ff; }}
            .section {{ margin-top:40px; }}
            .note {{ color:#8b949e; font-size:14px; }}
        </style>
    </head>
    <body>

    <h1>ReconBot Report</h1>
    <p><strong>Target IP:</strong> {target_ip}</p>

    <div class="section">
        <h2>Quick Nmap Scan (Top 1000 Ports)</h2>
        <pre style="background:#161b22;padding:15px;overflow:auto;">
{nmap_output}
        </pre>
    </div>

    <div class="section">
        <h2>Gobuster Results</h2>
        <table>
            <tr>
                <th>Port</th>
                <th>Status</th>
                <th>Path</th>
            </tr>
    """

    for base_url, results in gobuster_results.items():

        port = base_url.split(":")[-1]

        if not results:
            html += f"""
            <tr>
                <td>{port}</td>
                <td colspan="2">No paths found</td>
            </tr>
            """
        else:
            for item in results:
                status = item.get("status")
                path = item.get("path")

                if status == 200:
                    status_class = "status-200"
                elif status == 403:
                    status_class = "status-403"
                elif status == 404:
                    status_class = "status-404"
                else:
                    status_class = "status-other"

                full_url = item.get("url")

                html += f"""
                <tr>
                    <td>{port}</td>
                    <td class="{status_class}">{status}</td>
                    <td><a href="{full_url}" target="_blank" style="color:#58a6ff;">{path}</a></td>
                </tr>
                """

    html += """
        </table>
    </div>

    <div class="section">
        <h2>⚠ Potential Vulnerabilities (Manual Verification Required)</h2>
        <p class="note">
        Bu bölüm Nuclei entegrasyonu sonrası otomatik olarak doldurulacaktır.
        Tespit edilen bulgular kesin zafiyet anlamına gelmez ve manuel doğrulama gerektirir.
        </p>
        <table>
            <tr>
                <th>Endpoint</th>
                <th>Issue</th>
                <th>Severity</th>
                <th>Template</th>
            </tr>
    """

    if not nuclei_results:
        html += """
            <tr>
                <td colspan="4">Nuclei çalıştırılmadı veya target bulunamadı.</td>
            </tr>
        """
    else:
        status = nuclei_results.get("Status")
        findings = nuclei_results.get("Findings", [])
        error = nuclei_results.get("Error")

        if status == "Clean":
            html += """
            <tr>
                <td colspan="4">Nuclei herhangi bir zafiyet tespit etmedi.</td>
            </tr>
            """
        elif status == "Error":
            html += f"""
            <tr>
                <td colspan="4">Nuclei hata verdi: {error}</td>
            </tr>
            """
        elif status == "Partial":
            html += f"""
            <tr>
                <td colspan="4">Nuclei kısmi sonuç üretti. Hata: {error}</td>
            </tr>
            """
            for finding in findings:
                endpoint = finding.get("matched-at") or finding.get("matchedAt") or finding.get("host", "Unknown")
                issue = finding.get("info", {}).get("name", "Unknown")
                severity = finding.get("info", {}).get("severity", "Unknown")
                template = finding.get("templateID", "Unknown")

                html += f"""
                <tr>
                    <td>{endpoint}</td>
                    <td>{issue}</td>
                    <td>{severity}</td>
                    <td>{template}</td>
                </tr>
                """
        elif status == "Success":
            for finding in findings:
                endpoint = finding.get("matched-at") or finding.get("matchedAt") or finding.get("host", "Unknown")
                issue = finding.get("info", {}).get("name", "Unknown")
                severity = finding.get("info", {}).get("severity", "Unknown")
                template = finding.get("templateID", "Unknown")

                html += f"""
                <tr>
                    <td>{endpoint}</td>
                    <td>{issue}</td>
                    <td>{severity}</td>
                    <td>{template}</td>
                </tr>
                """

    html += """
        </table>
    </div>

    </body>
    </html>
    """

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[+] HTML report created: {report_path}")
    webbrowser.open(report_path.as_uri())

if __name__ == "__main__":
    main()