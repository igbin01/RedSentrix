CC = gcc
CFLAGS = -Wall -Wextra -O2 -fPIC
LDFLAGS = -shared

# Windows
ifeq ($(OS),Windows_NT)
	CC = x86_64-w64-mingw32-gcc
	CFLAGS += -D_WIN32
	LDFLAGS = -shared -Wl,--subsystem,windows
	EXT = .dll
else
	EXT = .so
endif

# Directories
INJECT_DIR = inject
EVASION_DIR = evasion
MEMORY_DIR = memory
PERSISTENCE_DIR = persistence
HIDE_DIR = hide
BUILD_DIR = ../build/stealth

# Source files
INJECT_SRC = $(INJECT_DIR)/inject.c
EVASION_SRC = $(EVASION_DIR)/evasion.c
MEMORY_SRC = $(MEMORY_DIR)/memory.c
PERSISTENCE_SRC = $(PERSISTENCE_DIR)/persistence.c
HIDE_SRC = $(HIDE_DIR)/hide.c

# Object files
INJECT_OBJ = $(BUILD_DIR)/inject.o
EVASION_OBJ = $(BUILD_DIR)/evasion.o
MEMORY_OBJ = $(BUILD_DIR)/memory.o
PERSISTENCE_OBJ = $(BUILD_DIR)/persistence.o
HIDE_OBJ = $(BUILD_DIR)/hide.o

# Libraries
INJECT_LIB = $(BUILD_DIR)/libinject$(EXT)
EVASION_LIB = $(BUILD_DIR)/libevasion$(EXT)
MEMORY_LIB = $(BUILD_DIR)/libmemory$(EXT)
PERSISTENCE_LIB = $(BUILD_DIR)/libpersistence$(EXT)
HIDE_LIB = $(BUILD_DIR)/libhide$(EXT)

.PHONY: all clean directories

all: directories $(INJECT_LIB) $(EVASION_LIB) $(MEMORY_LIB) $(PERSISTENCE_LIB) $(HIDE_LIB)

directories:
	@mkdir -p $(BUILD_DIR)

$(INJECT_LIB): $(INJECT_OBJ)
	$(CC) $(LDFLAGS) -o $@ $<

$(EVASION_LIB): $(EVASION_OBJ)
	$(CC) $(LDFLAGS) -o $@ $<

$(MEMORY_LIB): $(MEMORY_OBJ)
	$(CC) $(LDFLAGS) -o $@ $<

$(PERSISTENCE_LIB): $(PERSISTENCE_OBJ)
	$(CC) $(LDFLAGS) -o $@ $<

$(HIDE_LIB): $(HIDE_OBJ)
	$(CC) $(LDFLAGS) -o $@ $<

$(BUILD_DIR)/%.o: $(INJECT_DIR)/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD_DIR)/%.o: $(EVASION_DIR)/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD_DIR)/%.o: $(MEMORY_DIR)/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD_DIR)/%.o: $(PERSISTENCE_DIR)/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD_DIR)/%.o: $(HIDE_DIR)/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -rf $(BUILD_DIR)/*.o $(BUILD_DIR)/*.so $(BUILD_DIR)/*.dll

