"""
Custom exceptions for the distributed device control system.
"""


class DeviceControlSystemError(Exception):
    """Base exception for device control system errors."""
    pass


class DeviceRegistrationError(DeviceControlSystemError):
    """Raised when device registration fails."""
    pass


class DeviceTypeLimitExceededError(DeviceRegistrationError):
    """Raised when device type limit is exceeded."""
    pass


class InvalidDeviceTypeError(DeviceRegistrationError):
    """Raised when an invalid device type is provided."""
    pass


class DeviceNotFoundError(DeviceControlSystemError):
    """Raised when a device is not found in the registry."""
    pass


class DeviceCommunicationError(DeviceControlSystemError):
    """Raised when communication with a device fails."""
    pass


class ConfigurationError(DeviceControlSystemError):
    """Raised when configuration is invalid or missing."""
    pass


class NetworkError(DeviceControlSystemError):
    """Raised when network operations fail."""
    pass