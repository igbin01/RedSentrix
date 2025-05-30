#define _GNU_SOURCE
#include <stdarg.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/types.h>
#include <string.h>   // for strcmp()
#include <errno.h>    // for errno and ENOENT

static int (*real_open)(const char *pathname, int flags, ...) = NULL;

int open(const char *pathname, int flags, ...)
{
    if (!real_open) {
        real_open = dlsym(RTLD_NEXT, "open");
    }

    // Check if pathname is "/proc/self/maps"
    if (pathname && strcmp(pathname, "/proc/self/maps") == 0) {
        // Pretend file does not exist to hide memory maps
        errno = ENOENT;
        return -1;
    }

    va_list args;
    va_start(args, flags);

    int fd;
    if (flags & O_CREAT) {
        mode_t mode = va_arg(args, mode_t);
        fd = real_open(pathname, flags, mode);
    } else {
        fd = real_open(pathname, flags);
    }

    va_end(args);
    return fd;
}

