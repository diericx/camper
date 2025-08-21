"""
Background cleanup service for removing inactive devices from the registry.
"""

import threading
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from shared.constants import CLEANUP_INTERVAL
from shared.logging_config import log_system_event


class CleanupService:
    """
    Background service that periodically cleans up inactive devices.
    """
    
    def __init__(self, device_registry, logger=None, cleanup_interval=CLEANUP_INTERVAL):
        """
        Initialize the cleanup service.
        
        Args:
            device_registry: DeviceRegistry instance
            logger: Logger instance
            cleanup_interval (int): Cleanup interval in seconds
        """
        self.device_registry = device_registry
        self.logger = logger
        self.cleanup_interval = cleanup_interval
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self._lock = threading.Lock()
        
        if self.logger:
            log_system_event(
                self.logger, 'cleanup_service_init', 
                f"Cleanup service initialized with {cleanup_interval}s interval"
            )
    
    def start(self):
        """
        Start the cleanup service.
        """
        with self._lock:
            if self.is_running:
                if self.logger:
                    self.logger.warning("Cleanup service is already running")
                return
            
            try:
                # Add the cleanup job to the scheduler
                self.scheduler.add_job(
                    func=self._cleanup_task,
                    trigger=IntervalTrigger(seconds=self.cleanup_interval),
                    id='device_cleanup',
                    name='Device Registry Cleanup',
                    replace_existing=True
                )
                
                # Start the scheduler
                self.scheduler.start()
                self.is_running = True
                
                if self.logger:
                    log_system_event(
                        self.logger, 'cleanup_service_start',
                        f"Cleanup service started with {self.cleanup_interval}s interval"
                    )
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to start cleanup service: {e}")
                raise
    
    def stop(self):
        """
        Stop the cleanup service.
        """
        with self._lock:
            if not self.is_running:
                if self.logger:
                    self.logger.warning("Cleanup service is not running")
                return
            
            try:
                self.scheduler.shutdown(wait=True)
                self.is_running = False
                
                if self.logger:
                    log_system_event(
                        self.logger, 'cleanup_service_stop',
                        "Cleanup service stopped"
                    )
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error stopping cleanup service: {e}")
                raise
    
    def force_cleanup(self):
        """
        Force an immediate cleanup operation.
        
        Returns:
            List[str]: List of removed device IDs
        """
        if self.logger:
            log_system_event(
                self.logger, 'cleanup_force',
                "Manual cleanup triggered"
            )
        
        return self._cleanup_task()
    
    def _cleanup_task(self):
        """
        Internal cleanup task that removes inactive devices.
        
        Returns:
            List[str]: List of removed device IDs
        """
        try:
            start_time = time.time()
            
            # Get registry stats before cleanup
            stats_before = self.device_registry.get_registry_stats()
            
            # Perform cleanup
            removed_devices = self.device_registry.cleanup_inactive_devices()
            
            # Calculate cleanup duration
            cleanup_duration = round((time.time() - start_time) * 1000, 2)  # milliseconds
            
            # Log cleanup results
            if self.logger:
                log_system_event(
                    self.logger, 'cleanup_completed',
                    f"Cleanup completed in {cleanup_duration}ms",
                    removed_count=len(removed_devices),
                    devices_before=stats_before['total_devices'],
                    devices_after=stats_before['total_devices'] - len(removed_devices),
                    removed_devices=removed_devices if removed_devices else None
                )
            
            return removed_devices
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during cleanup task: {e}")
            return []
    
    def get_status(self):
        """
        Get the current status of the cleanup service.
        
        Returns:
            Dict[str, Any]: Service status information
        """
        with self._lock:
            status = {
                'is_running': self.is_running,
                'cleanup_interval': self.cleanup_interval,
                'scheduler_running': self.scheduler.running if hasattr(self.scheduler, 'running') else False,
                'next_run_time': None
            }
            
            if self.is_running and self.scheduler.running:
                try:
                    job = self.scheduler.get_job('device_cleanup')
                    if job and job.next_run_time:
                        status['next_run_time'] = job.next_run_time.isoformat()
                except Exception:
                    pass  # Ignore errors getting next run time
            
            return status
    
    def update_interval(self, new_interval):
        """
        Update the cleanup interval.
        
        Args:
            new_interval (int): New cleanup interval in seconds
        """
        with self._lock:
            if new_interval <= 0:
                raise ValueError("Cleanup interval must be positive")
            
            old_interval = self.cleanup_interval
            self.cleanup_interval = new_interval
            
            # If service is running, restart with new interval
            if self.is_running:
                try:
                    # Remove existing job
                    self.scheduler.remove_job('device_cleanup')
                    
                    # Add job with new interval
                    self.scheduler.add_job(
                        func=self._cleanup_task,
                        trigger=IntervalTrigger(seconds=new_interval),
                        id='device_cleanup',
                        name='Device Registry Cleanup',
                        replace_existing=True
                    )
                    
                    if self.logger:
                        log_system_event(
                            self.logger, 'cleanup_interval_updated',
                            f"Cleanup interval updated from {old_interval}s to {new_interval}s"
                        )
                        
                except Exception as e:
                    # Rollback on error
                    self.cleanup_interval = old_interval
                    if self.logger:
                        self.logger.error(f"Failed to update cleanup interval: {e}")
                    raise
            else:
                if self.logger:
                    log_system_event(
                        self.logger, 'cleanup_interval_updated',
                        f"Cleanup interval updated from {old_interval}s to {new_interval}s (service not running)"
                    )