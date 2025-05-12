# modules/recon_network_advanced.py
import socket
import psutil
import os
import platform
import subprocess

def run():
    print("\n🔍 Advanced Network Reconnaissance")
    result = []

    # Get all active network interfaces
    net_if_addrs = psutil.net_if_addrs()
    net_if_stats = psutil.net_if_stats()
    for iface, addrs in net_if_addrs.items():
        if iface in net_if_stats and net_if_stats[iface].isup:
            result.append(f"Interface: {iface}")
            for addr in addrs:
                result.append(f"  Address: {addr.address} ({addr.family.name})")

    # ARP Table
    try:
        arp_output = subprocess.check_output(['ip', 'neigh'], stderr=subprocess.DEVNULL).decode()
        result.append("\nARP Table:")
        result.extend(["  " + line for line in arp_output.strip().split('\n')])
    except Exception as e:
        result.append(f"[!] Failed to get ARP table: {e}")

    # Open ports and connections
    result.append("\nActive Connections:")
    for conn in psutil.net_connections(kind='inet'):
        laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else ""
        raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else ""
        status = conn.status
        pid = conn.pid
        try:
            proc_name = psutil.Process(pid).name() if pid else "N/A"
        except:
            proc_name = "N/A"
        result.append(f"  {laddr} -> {raddr} [{status}] (PID: {pid}, Proc: {proc_name})")

    return "\n".join(result)
