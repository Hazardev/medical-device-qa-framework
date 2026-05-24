"""
Medical Device Simulator
Simulates a basic medical device with software validation requirements.
Purpose: Demonstrate QA testing methodology for equipment with embedded software.
"""

from datetime import datetime
from typing import Dict, List, Optional


class MedicalDeviceSimulator:
    """
    Simulates a medical device requiring software validation per FDA guidelines.
    
    Key Validation Concepts:
    - State management (initialized, powered_on, ready, error)
    - Event logging for audit trail (21 CFR Part 11)
    - Self-diagnostic capabilities
    - Safety interlocks
    """
    
    # Valid device states per design specification
    VALID_STATES = ["initialized", "powered_on", "ready", "error"]
    
    def __init__(self):
        """Initialize device in safe default state"""
        self.device_state = "initialized"
        self.event_log: List[Dict] = []
        self.diagnostic_results: List[Dict] = []
        self.error_count = 0
        self._log_event("Device initialized", "SYSTEM")
    
    def power_on(self) -> bool:
        """
        Power on device with safety checks.
        
        Returns:
            bool: True if power-on successful, False otherwise
        """
        if self.device_state != "initialized":
            self._log_event("Power-on attempted from invalid state", "ERROR")
            return False
        
        # Simulate hardware checks
        hardware_ok = self._check_hardware()
        if not hardware_ok:
            self.device_state = "error"
            self._log_event("Hardware check failed during power-on", "ERROR")
            return False
        
        self.device_state = "powered_on"
        self._log_event("Device powered on successfully", "SYSTEM")
        return True
    
    def run_self_diagnostic(self) -> Dict:
        """
        Execute self-diagnostic test suite.
        
        Returns:
            Dict containing diagnostic results with timestamp and status
        """
        if self.device_state not in ["powered_on", "ready"]:
            result = {
                "status": "FAILED",
                "reason": "Device must be powered on to run diagnostics",
                "timestamp": datetime.now().isoformat()
            }
            self._log_event("Diagnostic attempted in invalid state", "ERROR")
            return result
        
        # Simulate diagnostic checks
        checks = {
            "memory_test": self._check_memory(),
            "sensor_calibration": self._check_sensors(),
            "communication_interface": self._check_communication(),
            "safety_interlocks": self._check_safety_systems()
        }
        
        all_passed = all(checks.values())
        
        result = {
            "status": "PASSED" if all_passed else "FAILED",
            "checks": checks,
            "timestamp": datetime.now().isoformat(),
            "device_state": self.device_state
        }
        
        self.diagnostic_results.append(result)
        self._log_event(f"Self-diagnostic completed: {result['status']}", "DIAGNOSTIC")
        
        if all_passed:
            self.device_state = "ready"
        else:
            self.device_state = "error"
            self.error_count += 1
        
        return result
    
    def get_device_state(self) -> str:
        """Return current device state"""
        return self.device_state
    
    def get_event_log(self) -> List[Dict]:
        """
        Return complete event log for audit purposes (21 CFR Part 11 compliance).
        
        Returns:
            List of all logged events with timestamps
        """
        return self.event_log.copy()
    
    def reset_device(self) -> bool:
        """Reset device to initialized state"""
        self._log_event("Device reset initiated", "SYSTEM")
        self.device_state = "initialized"
        self.error_count = 0
        return True
    
    # Private helper methods
    def _check_hardware(self) -> bool:
        """Simulate hardware status check"""
        return True  # Simplified for demo
    
    def _check_memory(self) -> bool:
        """Simulate memory test"""
        return True
    
    def _check_sensors(self) -> bool:
        """Simulate sensor calibration check"""
        return True
    
    def _check_communication(self) -> bool:
        """Simulate communication interface test"""
        return True
    
    def _check_safety_systems(self) -> bool:
        """Simulate safety interlock verification"""
        return True
    
    def _log_event(self, event: str, event_type: str) -> None:
        """
        Log event with timestamp for audit trail.
        Critical for 21 CFR Part 11 compliance.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "event_type": event_type,
            "device_state": self.device_state
        }
        self.event_log.append(log_entry)
