"""
Heartbeat service for device controllers.
Continuously registers with the main controller to maintain active status.
"""

import threading
import time
from datetime import datetime

from shared.constants import *
from shared.exceptions import *
from shared.logging_config import log_device_event, log_system_event


class HeartbeatService:
    """
    Service that sends periodic heartbeat messages to the main controller.
    """
    
    def __init__(self, device_controller, logger=None):
        """
        Initialize the heartbeat service.
        
        Args:
            device_controller: BaseDeviceController instance
            logger: Logger instance
        """
        self.device_controller = device_controller
        self.logger = logger
        self.is_running = False
        self._thread = None
        self._stop_event = threading.Event()
        
        # Get heartbeat configuration
        heartbeat_config = device_controller.config.get('heartbeat', {})
        self.interval = heartbeat_config.get('interval_seconds', DEFAULT_HEARTBEAT_INTERVAL)
        self.retry_attempts = heartbeat_config.get('retry_attempts', 3)
        self.retry_delay = heartbeat_config.get('retry_delay_seconds', 5)
        
        # Statistics
        self.heartbeat_count = 0
        self.failure_count = 0
        self.last_success = None
        self.last_failure = None
        
        if self.logger:
            log_system_event(
                self.logger, 'heartbeat_service_init',
                f"Heartbeat service initialized with {self.interval}s interval"
            )
    
    def start(self):
        """Start the heartbeat service."""
        if self.is_running:
            if self.logger:
                self.logger.warning("Heartbeat service is already running")
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        # Start heartbeat thread
        self._thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._thread.start()
        
        if self.logger:
            log_system_event(
                self.logger, 'heartbeat_service_start',
                f"Heartbeat service started with {self.interval}s interval"
            )
    
    def stop(self):
        """Stop the heartbeat service."""
        if not self.is_running:
            if self.logger:
                self.logger.warning("Heartbeat service is not running")
            return
        
        self.is_running = False
        self._stop_event.set()
        
        # Wait for thread to finish
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        
        if self.logger:
            log_system_event(
                self.logger, 'heartbeat_service_stop',
                "Heartbeat service stopped"
            )
    
    def _heartbeat_loop(self):
        """Main heartbeat loop that runs in a separate thread."""
        while self.is_running and not self._stop_event.is_set():
            try:
                # Send heartbeat
                self._send_heartbeat()
                
                # Wait for next interval or stop signal
                self._stop_event.wait(self.interval)
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Unexpected error in heartbeat loop: {e}")
                
                # Wait a bit before retrying to avoid tight error loops
                self._stop_event.wait(min(self.interval, 30))
    
    def _send_heartbeat(self):
        """Send a single heartbeat to the main controller."""
        device_id = self.device_controller.get_device_id()
        device_type = self.device_controller.get_device_type()
        
        for attempt in range(self.retry_attempts):
            try:
                # Attempt to register (which serves as heartbeat)
                success = self.device_controller.register_with_main_controller()
                
                if success:
                    self.heartbeat_count += 1
                    self.last_success = datetime.now()
                    
                    if self.logger:
                        log_device_event(
                            self.logger, 'heartbeat_success', device_id, device_type,
                            heartbeat_count=self.heartbeat_count,
                            attempt=attempt + 1
                        )
                    
                    return  # Success, exit retry loop
                else:
                    raise DeviceRegistrationError("Registration returned False")
            
            except (DeviceRegistrationError, DeviceCommunicationError) as e:
                self.failure_count += 1
                self.last_failure = datetime.now()
                
                if self.logger:
                    log_device_event(
                        self.logger, 'heartbeat_failure', device_id, device_type,
                        error=str(e),
                        attempt=attempt + 1,
                        max_attempts=self.retry_attempts,
                        failure_count=self.failure_count
                    )
                
                # If this was the last attempt, log final failure
                if attempt == self.retry_attempts - 1:
                    if self.logger:
                        log_device_event(
                            self.logger, 'heartbeat_failed_all_attempts', device_id, device_type,
                            total_attempts=self.retry_attempts,
                            error=str(e)
                        )
                    break
                else:
                    # Wait before retrying
                    if not self._stop_event.wait(self.retry_delay):
                        continue  # Continue if not stopping
                    else:
                        break  # Exit if stopping
            
            except Exception as e:
                self.failure_count += 1
                self.last_failure = datetime.now()
                
                if self.logger:
                    self.logger.error(f"Unexpected error during heartbeat: {e}")
                break
    
    def force_heartbeat(self):
        """
        Force an immediate heartbeat outside of the normal schedule.
        
        Returns:
            bool: True if heartbeat was successful
        """
        if self.logger:
            log_system_event(
                self.logger, 'heartbeat_force',
                "Manual heartbeat triggered"
            )
        
        try:
            self._send_heartbeat()
            return self.last_success is not None and (
                self.last_failure is None or self.last_success > self.last_failure
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during forced heartbeat: {e}")
            return False
    
    def get_status(self):
        """
        Get the current status of the heartbeat service.
        
        Returns:
            Dict[str, Any]: Service status information
        """
        status = {
            'is_running': self.is_running,
            'interval_seconds': self.interval,
            'retry_attempts': self.retry_attempts,
            'retry_delay_seconds': self.retry_delay,
            'statistics': {
                'heartbeat_count': self.heartbeat_count,
                'failure_count': self.failure_count,
                'last_success': self.last_success.isoformat() if self.last_success else None,
                'last_failure': self.last_failure.isoformat() if self.last_failure else None
            }
        }
        
        # Calculate health status
        if self.last_success is None:
            status['health'] = 'never_succeeded'
        elif self.last_failure is None or self.last_success > self.last_failure:
            status['health'] = 'healthy'
        else:
            # Calculate time since last success
            time_since_success = datetime.now() - self.last_success
            if time_since_success.total_seconds() > self.interval * 3:
                status['health'] = 'unhealthy'
            else:
                status['health'] = 'degraded'
        
        return status
    
    def update_interval(self, new_interval):
        """
        Update the heartbeat interval.
        
        Args:
            new_interval (int): New interval in seconds
        """
        if new_interval <= 0:
            raise ValueError("Heartbeat interval must be positive")
        
        old_interval = self.interval
        self.interval = new_interval
        
        if self.logger:
            log_system_event(
                self.logger, 'heartbeat_interval_updated',
                f"Heartbeat interval updated from {old_interval}s to {new_interval}s"
            )
    
    def reset_statistics(self):
        """Reset heartbeat statistics."""
        self.heartbeat_count = 0
        self.failure_count = 0
        self.last_success = None
        self.last_failure = None
        
        if self.logger:
            log_system_event(
                self.logger, 'heartbeat_stats_reset',
                "Heartbeat statistics reset"
            )