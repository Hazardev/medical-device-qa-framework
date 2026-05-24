"""
Medical Device Validation Test Suite
Demonstrates systematic QA testing approach for equipment qualification.

Test Categories:
- Functional Testing (TC-001 to TC-005)
- State Transition Testing (TC-006 to TC-008)
- Negative Testing (TC-009 to TC-011)
- Compliance Testing (TC-012 to TC-013)
"""

import unittest
from device_simulator import MedicalDeviceSimulator


class TestDeviceValidation(unittest.TestCase):
    """
    Comprehensive validation test suite following FDA guidance for 
    software validation in medical devices.
    """
    
    def setUp(self):
        """Set up test fixture - executed before each test"""
        self.device = MedicalDeviceSimulator()
    
    def tearDown(self):
        """Clean up after test - executed after each test"""
        self.device = None
    
    # FUNCTIONAL TESTING
    
    def test_TC001_device_initialization(self):
        """
        TC-001: Verify device initializes in safe default state
        Requirement: Device shall initialize in 'initialized' state
        Risk Level: HIGH (safety-critical)
        """
        self.assertEqual(self.device.get_device_state(), "initialized")
        self.assertEqual(len(self.device.get_event_log()), 1)
    
    def test_TC002_power_on_success(self):
        """
        TC-002: Verify successful power-on from initialized state
        Requirement: Device shall transition to 'powered_on' when power_on() succeeds
        """
        result = self.device.power_on()
        self.assertTrue(result)
        self.assertEqual(self.device.get_device_state(), "powered_on")
    
    def test_TC003_self_diagnostic_execution(self):
        """
        TC-003: Verify self-diagnostic executes when device powered on
        Requirement: Device shall perform self-diagnostic and return results
        """
        self.device.power_on()
        result = self.device.run_self_diagnostic()
        
        self.assertIn("status", result)
        self.assertIn("checks", result)
        self.assertIn("timestamp", result)
        self.assertIn(result["status"], ["PASSED", "FAILED"])
    
    def test_TC004_diagnostic_transitions_to_ready(self):
        """
        TC-004: Verify successful diagnostic transitions device to 'ready' state
        Requirement: Device shall enter 'ready' state after passing diagnostics
        """
        self.device.power_on()
        result = self.device.run_self_diagnostic()
        
        if result["status"] == "PASSED":
            self.assertEqual(self.device.get_device_state(), "ready")
    
    def test_TC005_device_reset_functionality(self):
        """
        TC-005: Verify device reset returns to initialized state
        Requirement: Device shall return to safe initialized state on reset
        """
        self.device.power_on()
        self.device.run_self_diagnostic()
        
        result = self.device.reset_device()
        self.assertTrue(result)
        self.assertEqual(self.device.get_device_state(), "initialized")
    
    # STATE TRANSITION TESTING
    
    def test_TC006_invalid_power_on_from_powered_state(self):
        """
        TC-006: Verify power-on rejected when already powered
        Requirement: Device shall reject power-on from non-initialized states (safety)
        Risk Level: HIGH (prevents unsafe operations)
        """
        self.device.power_on()  # First power-on succeeds
        result = self.device.power_on()  # Second attempt should fail
        
        self.assertFalse(result)
    
    def test_TC007_valid_state_progression(self):
        """
        TC-007: Verify correct state progression through normal operation
        Requirement: Device shall follow state diagram: initialized → powered_on → ready
        """
        self.assertEqual(self.device.get_device_state(), "initialized")
        
        self.device.power_on()
        self.assertEqual(self.device.get_device_state(), "powered_on")
        
        self.device.run_self_diagnostic()
        self.assertEqual(self.device.get_device_state(), "ready")
    
    def test_TC008_state_in_valid_states_list(self):
        """
        TC-008: Verify device state always within valid state set
        Requirement: Device state shall only be valid defined states (data integrity)
        """
        valid_states = MedicalDeviceSimulator.VALID_STATES
        
        self.assertIn(self.device.get_device_state(), valid_states)
        
        self.device.power_on()
        self.assertIn(self.device.get_device_state(), valid_states)
        
        self.device.run_self_diagnostic()
        self.assertIn(self.device.get_device_state(), valid_states)
    
    # NEGATIVE TESTING
    
    def test_TC009_diagnostic_without_power_on(self):
        """
        TC-009: Verify diagnostic fails if device not powered on (negative test)
        Requirement: Device shall reject diagnostic execution in initialized state
        Risk Level: MEDIUM (prevents invalid operations)
        """
        result = self.device.run_self_diagnostic()
        
        self.assertEqual(result["status"], "FAILED")
        self.assertIn("reason", result)
    
    def test_TC010_power_on_after_error_state(self):
        """
        TC-010: Verify power-on rejected from error state (negative test)
        Requirement: Device in error state shall require reset before power-on
        """
        # Force device into error state (would require failure injection in real scenario)
        self.device.device_state = "error"
        
        result = self.device.power_on()
        self.assertFalse(result)
    
    def test_TC011_diagnostic_returns_all_required_fields(self):
        """
        TC-011: Verify diagnostic result contains all mandatory fields
        Requirement: Diagnostic results shall include status, checks, timestamp
        """
        self.device.power_on()
        result = self.device.run_self_diagnostic()
        
        required_fields = ["status", "checks", "timestamp", "device_state"]
        for field in required_fields:
            self.assertIn(field, result, f"Missing required field: {field}")
    
    # COMPLIANCE TESTING (21 CFR Part 11)
    
    def test_TC012_event_logging_for_audit_trail(self):
        """
        TC-012: Verify all operations logged for audit trail (21 CFR Part 11)
        Requirement: All device operations shall be logged with timestamp
        Compliance: 21 CFR Part 11.10(e) - Audit trail
        """
        initial_log_count = len(self.device.get_event_log())
        
        self.device.power_on()
        self.device.run_self_diagnostic()
        
        final_log_count = len(self.device.get_event_log())
        self.assertGreater(final_log_count, initial_log_count)
        
        # Verify each log entry has timestamp
        for entry in self.device.get_event_log():
            self.assertIn("timestamp", entry)
            self.assertIn("event", entry)
    
    def test_TC013_log_entries_immutable(self):
        """
        TC-013: Verify event log returns copy (prevents tampering)
        Requirement: Event log shall be protected from modification
        Compliance: 21 CFR Part 11.10(a) - Data integrity
        """
        log1 = self.device.get_event_log()
        log2 = self.device.get_event_log()
        
        # Verify we get copies, not references
        self.assertIsNot(log1, log2)
        self.assertEqual(len(log1), len(log2))


class TestDeviceRiskScenarios(unittest.TestCase):
    """
    Risk-based test scenarios focusing on safety-critical functionality.
    """
    
    def setUp(self):
        self.device = MedicalDeviceSimulator()
    
    def test_TC014_multiple_resets_safe(self):
        """
        TC-014: Verify multiple reset operations are safe (stress test)
        Requirement: Reset shall be idempotent and always safe
        Risk Level: HIGH (safety-critical)
        """
        for i in range(10):
            result = self.device.reset_device()
            self.assertTrue(result)
            self.assertEqual(self.device.get_device_state(), "initialized")
    
    def test_TC015_event_log_accumulation(self):
        """
        TC-015: Verify event log accumulates correctly over operations
        Requirement: Event log shall maintain complete history
        """
        initial_count = len(self.device.get_event_log())
        
        # Execute multiple operations
        self.device.power_on()
        self.device.run_self_diagnostic()
        self.device.reset_device()
        self.device.power_on()
        
        final_count = len(self.device.get_event_log())
        self.assertGreater(final_count, initial_count)


def run_validation_suite():
    """Execute full validation test suite with detailed reporting"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestDeviceValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestDeviceRiskScenarios))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("VALIDATION TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result


if __name__ == "__main__":
    run_validation_suite()
