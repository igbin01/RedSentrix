/*
 * RedSentrix - Hiding Module (C)
 * Process and file hiding
 */

#ifdef _WIN32
#include <windows.h>
#include <tlhelp32.h>

/*
 * Hide process from task manager
 */
int hide_process(pid_t pid) {
    // Process hiding implementation
    // This would involve hooking system calls or modifying process list
    return 0;
}

/*
 * Hide file from directory listing
 */
int hide_file(const char *filepath) {
    DWORD attributes = GetFileAttributesA(filepath);
    if (attributes == INVALID_FILE_ATTRIBUTES) {
        return -1;
    }
    
    // Set hidden and system attributes
    attributes |= FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM;
    return SetFileAttributesA(filepath, attributes) ? 0 : -1;
}
#endif

