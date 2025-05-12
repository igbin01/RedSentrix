# core/memory/scanner.py

import psutil
import ctypes
import os
import re
from core.memory.models import MemoryRegion, TargetProcess
from core.memory.stealth_utils import stealth_log

class MemoryScanner:
    def __init__(self, config):
        self.config = config

    def list_target_processes(self):
        """List all processes that are not system-critical and are potential injection targets."""
        target_procs = []

        for proc in psutil.process_iter(['pid', 'name', 'username']):
            try:
                if self._is_suspicious_process(proc):
                    target_procs.append(TargetProcess(proc.pid, proc.name()))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return target_procs

    def _is_suspicious_process(self, proc):
        """Heuristics to filter system vs non-system processes"""
        name = proc.info['name'] or ""
        username = proc.info.get('username', '')

        # Ignore root/system daemons unless explicitly enabled
        if username in ("root", "SYSTEM") and not self.config.include_root_processes:
            return False

        # Filter out known good processes
        known_safe = ['sshd', 'init', 'systemd', 'cron', 'bash', 'zsh', 'explorer.exe']
        if any(ks in name.lower() for ks in known_safe):
            return False

        return True

    def get_memory_regions(self, target_proc):
        """Extract memory map for a given process ID and filter based on scan criteria."""
        pid = target_proc.pid
        regions = []

        maps_path = f"/proc/{pid}/maps"
        mem_path = f"/proc/{pid}/mem"

        if not os.path.exists(maps_path) or not os.path.exists(mem_path):
            stealth_log(f"[x] Cannot access memory of PID {pid}", level="debug")
            return regions

        try:
            with open(maps_path, 'r') as maps_file:
                for line in maps_file:
                    region = self._parse_maps_line(line)
                    if region and self._is_suspicious_region(region):
                        regions.append(region)

            return regions
        except Exception as e:
            stealth_log(f"[!] Failed reading memory maps for {pid}: {e}", level="debug")
            return []

    def _parse_maps_line(self, line):
        """Parses a line from /proc/PID/maps into a MemoryRegion object"""
        try:
            addr_range, perms, offset, dev, inode, *pathname = line.strip().split()
            start, end = [int(x, 16) for x in addr_range.split('-')]

            return MemoryRegion(
                start=start,
                end=end,
                perms=perms,
                pathname=' '.join(pathname) if pathname else ''
            )
        except Exception:
            return None

    def _is_suspicious_region(self, region):
        """Detect memory regions with RWX permissions or unknown pathnames"""
        if "x" in region.perms and "w" in region.perms:
            return True  # Likely shellcode or injected payload
        if region.pathname == "" and "x" in region.perms:
            return True  # Executable with no backing file (e.g., injected)
        if "[stack]" in region.pathname or "[heap]" in region.pathname:
            return False
        return False
