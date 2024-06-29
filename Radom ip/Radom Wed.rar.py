import os
import requests
import subprocess
from ipaddress import ip_network
from concurrent.futures import ThreadPoolExecutor, as_completed

# List of starting IP addresses
ip_list = [
    "45.137.245.0", "103.91.204.0", "43.255.241.0", "45.91.134.0", "103.91.206.0",
    "103.91.207.0", "103.233.194.0", "103.70.5.0", "103.141.69.0", "104.21.94.0",
    "150.107.30.0", "147.50.253.0", "154.202.2.0", "150.107.31.0", "154.202.3.0",
    "154.202.4.0", "154.16.7.0", "103.70.5.0", "103.91.205.0", "103.233.195.0",
    "103.91.189.0", "103.233.193.0", "103.253.73.0", "103.24.19.0", "103.212.180.0",
    "103.82.249.0", "103.253.73.0", "103.246.19.0", "103.141.68.0", "104.21.30.0",
    "172.67.207.0", "172.67.152.0", "172.67.187.0", "203.159.93.0", "43.229.135.0",
    "188.212.158.0", "43.254.132.0"
]

def check_ip(ip, url_path):
    # Check if the file at the given URL path is responsive
    url = f"http://{ip}{url_path}"
    try:
        response = requests.head(url, timeout=2)  # Use HEAD request to check response without loading data
        if response.status_code == 200:
            return ip
    except requests.RequestException:
        pass
    return None

def scan_ips_concurrently(ip_start, url_path):
    # Scan the IP range concurrently to check for responsive files
    network = ip_network(f"{ip_start}/24", strict=False)
    responsive_ips = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_ip = {executor.submit(check_ip, str(ip), url_path): ip for ip in network}
        for future in as_completed(future_to_ip):
            result = future.result()
            if result:
                responsive_ips.append(result)
                print(f"{result} is responsive")

    # Save responsive IPs to a file
    with open("responsive_ips.txt", "a") as file:
        for ip in responsive_ips:
            file.write(f"{ip}\n")

    return responsive_ips

def create_and_run_batch_script(responsive_ips):
    # Create and run a batch script to open responsive URLs in Google Chrome
    output_filename = "download_warz.bat"
    with open(output_filename, "w") as file:
        file.write("@echo off\n")
        for ip in responsive_ips:
            url = f"http://{ip}/Wed.rar"
            file.write(f'start chrome "{url}"\n')

    # Run the batch script
    subprocess.run([output_filename], check=True, shell=True)

def main():
    url_path = "/Wed.rar"
    all_responsive_ips = []
    for ip_start in ip_list:
        responsive_ips = scan_ips_concurrently(ip_start, url_path)
        all_responsive_ips.extend(responsive_ips)

    if all_responsive_ips:
        create_and_run_batch_script(all_responsive_ips)

if __name__ == "__main__":
    main()
