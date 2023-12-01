from enum import Enum

__all__ = (
    "TwoFactorBackupCodesStockEnum",
)


class TwoFactorBackupCodesStockEnum(Enum):
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"
