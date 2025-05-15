# nebula_core/memory/models.py

from dataclasses import dataclass, field
from typing import List, Optional
import enum
import time


class AccessType(enum.Enum):
    READ = "r"
    WRITE = "w"
    EXECUTE = "x"
    PRIVATE = "p"
    SHARED = "s"
    NONE = "-"


@dataclass
class MemoryRegion:
    start: int
    end: int
    permissions: List[AccessType]
    offset: Optional[int] = 0
    device: Optional[str] = None
    inode: Optional[int] = None
    pathname: Optional[str] = None

    @property
    def size(self) -> int:
        return self.end - self.start

    def is_executable(self) -> bool:
        return AccessType.EXECUTE in self.permissions

    def is_writable(self) -> bool:
        return AccessType.WRITE in self.permissions

    def is_readable(self) -> bool:
        return AccessType.READ in self.permissions


@dataclass
class ScanResult:
    region: MemoryRegion
    suspicious_patterns: List[str]
    entropy_score: Optional[float] = None
    matched_signatures: Optional[List[str]] = field(default_factory=list)
    timestamp: float = field(default_factory=lambda: time.time())


@dataclass
class ProcessFilter:
    name: Optional[str] = None
    pid: Optional[int] = None
    exclude_system: bool = True
    include_executables_only: bool = True
