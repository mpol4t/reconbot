# ReconBot

ReconBot, penetration testing ve CTF ortamlarında reconnaissance (keşif) ve enumeration süreçlerini otomatikleştirmek amacıyla Python ile geliştirilmiş modüler bir güvenlik aracıdır.

Bu araç, hedef sistemler üzerinde manuel olarak yapılan keşif adımlarını otomatik hale getirerek penetration testing sürecini hızlandırmayı ve daha verimli hale getirmeyi amaçlar.

---

## Özellikler

ReconBot aşağıdaki işlemleri otomatik olarak gerçekleştirir:

- Hedef sistemin erişilebilir olup olmadığını kontrol eder
- Nmap kullanarak port taraması yapar
- Web servisi tespit ederse Gobuster ile dizin keşfi yapar
- Nuclei kullanarak bilinen zafiyetlere karşı otomatik tarama gerçekleştirir
- Enumeration sürecini standartlaştırır ve hızlandırır
- Modüler yapısı sayesinde kolayca geliştirilebilir

---

## Mimari

ReconBot aşağıdaki keşif akışını otomatik olarak uygular:

Hedef
│
├─ Host erişim kontrolü
│
├─ Nmap port taraması
│
├─ Web servis tespiti
│ └─ Gobuster dizin taraması
│
└─ Nuclei zafiyet taraması

---

## Kullanılan Teknolojiler

- Python 3
- Nmap
- Gobuster
- Nuclei
- CLI (Command Line Interface)
- Modüler Python mimarisi

---

## Kurulum ve Çalıştırma

ReconBot iki farklı şekilde çalıştırılabilir:

## Yöntem 1 — pipx ile kurulum (Önerilen)

Bu yöntem ReconBot’u sisteminize global CLI tool olarak kurar ve her yerden çalıştırmanızı sağlar.

Kurulum:

pipx install -e .

Kurulumdan sonra ReconBot’u herhangi bir dizinden çalıştırabilirsiniz:

reconbot 10.10.10.10 -w wordlist.txt

Bu yöntem önerilir çünkü ReconBot’u sistem genelinde erişilebilir hale getirir.

## Yöntem 2 — Python module olarak çalıştırma (Kurulum gerektirmez)

Eğer pipx ile kurulum yapmak istemiyorsanız, ReconBot’u proje dizini içinden şu şekilde çalıştırabilirsiniz:

python -m reconbot.cli 10.10.10.10 -w wordlist.txt

Not: Bu yöntemde komut, proje klasörü içinden çalıştırılmalıdır.

---

## Gereksinimler

Aşağıdaki araçların sistemde kurulu olması gerekmektedir:
	•	Python 3.9+
	•	Nmap
	•	Gobuster
	•	Nuclei

---

## Kullanım

Temel kullanım:

python -m reconbot <target-ip> -w <wordlist>

Örnek:

python -m reconbot 10.10.10.10 -w /usr/share/wordlists/common.txt

---

## Amaç


Bu proje aşağıdaki amaçlarla geliştirilmiştir:
	•	Penetration testing süreçlerinde reconnaissance aşamasını otomatikleştirmek
	•	Enumeration sürecini hızlandırmak
	•	Güvenlik araçlarının çalışma mantığını daha derinlemesine öğrenmek
	•	Python ile güvenlik otomasyon araçları geliştirmek

---

## Uyarı

Bu araç yalnızca eğitim amaçlı ve yetkili olduğunuz sistemlerde test amacıyla kullanılmalıdır.

Yetkisiz sistemlere karşı kullanımı yasadışıdır.

---

## Geliştirici

Muhammed Polat Yağcı
Cybersecurity Student
GitHub: https://github.com/mpol4t
