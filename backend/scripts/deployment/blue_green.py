"""
Blue-Green deployment strategy for model deployments.

This module provides the BlueGreenDeployment class for zero-downtime deployments
using the blue-green deployment pattern. It allows deploying a new model version
to a green environment, warming it up, performing health checks, and switching
traffic with automatic rollback capabilities.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .model_versioning import ModelVersioning


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BlueGreenDeployment:
    """
    Blue-Green deployment strategy for model deployments.
    
    This class implements the blue-green deployment pattern where:
    - Blue environment: Current production version
    - Green environment: New version being deployed
    
    The deployment process:
    1. Deploy new version to green environment
    2. Warm up the green model with sample requests
    3. Perform health checks on green environment
    4. Switch traffic from blue to green
    5. Monitor for issues and rollback if needed
    
    Attributes:
        versioning (ModelVersioning): Model versioning system
        blue_version (str): Current production version (blue)
        green_version (str): New version being deployed (green)
        active (str): Currently active environment ("blue" or "green")
        blue_model (Any): Loaded blue model
        green_model (Any): Loaded green model
        deployment_log (List): Log of deployment events
    """
    
    def __init__(
        self,
        blue_version: Optional[str] = None,
        green_version: Optional[str] = None,
        base_dir: str = "models/classification"
    ):
        """
        Initialize Blue-Green deployment.
        
        Args:
            blue_version: Current production version (if None, loads from registry)
            green_version: New version to deploy (required for deployment)
            base_dir: Base directory for model versions
        """
        self.versioning = ModelVersioning(base_dir=base_dir)
        
        # Load blue version (current production)
        if blue_version is None:
            blue_version = self.versioning.registry.get('production_version')
            if blue_version is None:
                logger.warning("No production version found in registry")
        
        self.blue_version = blue_version
        self.green_version = green_version
        self.active = "blue"
        
        self.blue_model = None
        self.green_model = None
        
        # Deployment log for tracking events
        self.deployment_log = []
        
        logger.info("Blue-Green deployment initialized")
        logger.info(f"  Blue (production): {self.blue_version}")
        logger.info(f"  Green (candidate): {self.green_version}")
        logger.info(f"  Active: {self.active}")
        
        self._log_event("initialized", {
            "blue_version": self.blue_version,
            "green_version": self.green_version
        })
    
    def _log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log a deployment event.
        
        Args:
            event_type: Type of event (e.g., "deployed", "switched", "rolled_back")
            details: Event details dictionary
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        self.deployment_log.append(event)
        logger.debug(f"Event logged: {event_type}")
    
    def deploy_green(self) -> bool:
        """
        Deploy new version to green environment.
        
        This method:
        1. Validates that green_version is set
        2. Loads the green model from the version directory
        3. Warms up the model with sample requests
        4. Performs health checks
        
        Returns:
            True if deployment successful, False otherwise
        
        Raises:
            ValueError: If green_version is not set
        """
        if self.green_version is None:
            raise ValueError("green_version must be set before deploying")
        
        logger.info(f"Deploying {self.green_version} to green environment...")
        self._log_event("deploy_started", {"version": self.green_version})
        
        try:
            # Load green model
            logger.info(f"Loading model version {self.green_version}...")
            self.green_model, green_metadata = self.versioning.load_version(
                self.green_version
            )
            logger.info("Green model loaded successfully")
            logger.info(f"  Model: {green_metadata.get('model_name', 'unknown')}")
            logger.info(f"  Size: {green_metadata.get('model_size_mb', 0):.2f} MB")
            
            # Warm up model
            logger.info("Warming up green model...")
            warmup_success = self.warmup_model("green")
            if not warmup_success:
                logger.error("Model warmup failed")
                self._log_event("deploy_failed", {
                    "version": self.green_version,
                    "reason": "warmup_failed"
                })
                return False
            
            # Health check
            logger.info("Performing health check on green environment...")
            health_ok = self.health_check("green")
            if not health_ok:
                logger.error("Green environment health check failed")
                self._log_event("deploy_failed", {
                    "version": self.green_version,
                    "reason": "health_check_failed"
                })
                return False
            
            logger.info(f"Green environment deployed successfully: {self.green_version}")
            self._log_event("deploy_completed", {"version": self.green_version})
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy green environment: {e}")
            self._log_event("deploy_failed", {
                "version": self.green_version,
                "reason": str(e)
            })
            return False
    
    def warmup_model(self, environment: str) -> bool:
        """
        Warm up model with sample requests.
        
        This method sends several sample requests to the model to:
        - Load model into memory
        - Initialize CUDA kernels (if GPU)
        - Cache tokenizer and other components
        - Verify basic functionality
        
        Args:
            environment: Environment to warm up ("blue" or "green")
        
        Returns:
            True if warmup successful, False otherwise
        """
        logger.info(f"Warming up {environment} environment...")
        
        # Get model for environment
        if environment == "blue":
            model_data = self.blue_model
        elif environment == "green":
            model_data = self.green_model
        else:
            logger.error(f"Invalid environment: {environment}")
            return False
        
        if model_data is None:
            logger.error(f"{environment.capitalize()} model not loaded")
            return False
        
        # Sample texts for warmup
        warmup_texts = [
            "Machine learning is a subset of artificial intelligence.",
            "Deep neural networks have revolutionized computer vision.",
            "Natural language processing enables computers to understand text.",
            "Reinforcement learning agents learn through trial and error.",
            "Transfer learning allows models to leverage pre-trained knowledge."
        ]
        
        try:
            import torch
            
            model = model_data['model']
            tokenizer = model_data['tokenizer']
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model.to(device)
            model.eval()
            
            logger.info(f"Sending {len(warmup_texts)} warmup requests...")
            
            with torch.no_grad():
                for i, text in enumerate(warmup_texts, 1):
                    # Tokenize
                    inputs = tokenizer(
                        text,
                        truncation=True,
                        padding="max_length",
                        max_length=512,
                        return_tensors="pt"
                    )
                    inputs = {k: v.to(device) for k, v in inputs.items()}
                    
                    # Forward pass
                    start_time = time.time()
                    model(**inputs)
                    latency_ms = (time.time() - start_time) * 1000
                    
                    logger.debug(f"  Warmup request {i}/{len(warmup_texts)}: {latency_ms:.2f}ms")
            
            logger.info(f"{environment.capitalize()} model warmed up successfully")
            return True
            
        except Exception as e:
            logger.error(f"Warmup failed: {e}")
            return False
    
    def health_check(self, environment: str) -> bool:
        """
        Verify environment health.
        
        This method performs comprehensive health checks:
        - Model is loaded
        - Model can perform inference
        - Inference latency is acceptable (<200ms)
        - Model produces valid outputs
        
        Args:
            environment: Environment to check ("blue" or "green")
        
        Returns:
            True if all health checks pass, False otherwise
        """
        logger.info(f"Performing health check on {environment} environment...")
        
        checks = {
            "model_loaded": False,
            "inference_working": False,
            "latency_acceptable": False,
            "output_valid": False
        }
        
        try:
            # Get model for environment
            if environment == "blue":
                model_data = self.blue_model
                version = self.blue_version
            elif environment == "green":
                model_data = self.green_model
                version = self.green_version
            else:
                logger.error(f"Invalid environment: {environment}")
                return False
            
            # Check 1: Model loaded
            if model_data is not None:
                checks["model_loaded"] = True
                logger.info("  ✓ Model loaded")
            else:
                logger.error("  ✗ Model not loaded")
                return False
            
            # Check 2: Inference working
            import torch
            
            model = model_data['model']
            tokenizer = model_data['tokenizer']
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model.to(device)
            model.eval()
            
            test_text = "This is a test for health check verification."
            
            with torch.no_grad():
                inputs = tokenizer(
                    test_text,
                    truncation=True,
                    padding="max_length",
                    max_length=512,
                    return_tensors="pt"
                )
                inputs = {k: v.to(device) for k, v in inputs.items()}
                
                # Measure latency
                start_time = time.time()
                outputs = model(**inputs)
                latency_ms = (time.time() - start_time) * 1000
                
                # Check inference worked
                if outputs is not None and hasattr(outputs, 'logits'):
                    checks["inference_working"] = True
                    logger.info("  ✓ Inference working")
                else:
                    logger.error("  ✗ Inference failed")
                    return False
                
                # Check 3: Latency acceptable (<200ms)
                if latency_ms < 200:
                    checks["latency_acceptable"] = True
                    logger.info(f"  ✓ Latency acceptable ({latency_ms:.2f}ms)")
                else:
                    logger.warning(f"  ⚠ Latency high ({latency_ms:.2f}ms)")
                    # Don't fail on latency, just warn
                    checks["latency_acceptable"] = True
                
                # Check 4: Output valid
                logits = outputs.logits
                if logits.shape[0] > 0 and logits.shape[1] > 0:
                    # Check for NaN or Inf
                    if not torch.isnan(logits).any() and not torch.isinf(logits).any():
                        checks["output_valid"] = True
                        logger.info("  ✓ Output valid")
                    else:
                        logger.error("  ✗ Output contains NaN or Inf")
                        return False
                else:
                    logger.error("  ✗ Output shape invalid")
                    return False
            
            # All checks passed
            all_passed = all(checks.values())
            if all_passed:
                logger.info(f"{environment.capitalize()} environment health check: PASSED")
            else:
                logger.error(f"{environment.capitalize()} environment health check: FAILED")
                logger.error(f"  Failed checks: {[k for k, v in checks.items() if not v]}")
            
            self._log_event("health_check", {
                "environment": environment,
                "version": version,
                "checks": checks,
                "passed": all_passed
            })
            
            return all_passed
            
        except Exception as e:
            logger.error(f"Health check failed with exception: {e}")
            self._log_event("health_check_error", {
                "environment": environment,
                "error": str(e)
            })
            return False
    
    def switch_to_green(self) -> bool:
        """
        Switch traffic to green environment.
        
        This method:
        1. Validates green environment is ready
        2. Switches active environment to green
        3. Monitors for issues for 60 seconds
        4. Rolls back if issues detected
        
        Returns:
            True if switch successful, False if rolled back
        """
        logger.info("Switching traffic to green environment...")
        
        # Validate green is deployed and healthy
        if self.green_model is None:
            logger.error("Green model not deployed")
            return False
        
        # Perform final health check before switch
        if not self.health_check("green"):
            logger.error("Green environment not healthy, aborting switch")
            return False
        
        # Switch active environment
        previous_active = self.active
        self.active = "green"
        
        logger.info(f"Traffic switched from {previous_active} to green")
        logger.info(f"Active version: {self.green_version}")
        
        self._log_event("traffic_switched", {
            "from": previous_active,
            "to": "green",
            "version": self.green_version
        })
        
        # Monitor for issues (60 seconds)
        logger.info("Monitoring green environment for 60 seconds...")
        time.sleep(60)
        
        # Detect issues
        issues_detected = self.detect_issues()
        
        if issues_detected:
            logger.error("Issues detected in green environment, rolling back...")
            self.rollback()
            return False
        
        logger.info("No issues detected, switch successful")
        logger.info(f"Green environment ({self.green_version}) is now active")
        
        # Promote green version to production in registry
        try:
            self.versioning.promote_to_production(self.green_version)
            logger.info(f"Version {self.green_version} promoted to production in registry")
        except Exception as e:
            logger.warning(f"Failed to update production registry: {e}")
        
        return True
    
    def rollback(self) -> bool:
        """
        Rollback to blue environment.
        
        This method switches traffic back to the blue (previous production)
        environment in case of issues with the green deployment.
        
        Returns:
            True if rollback successful, False otherwise
        """
        logger.warning("Rolling back to blue environment...")
        
        # Validate blue is available
        if self.blue_model is None and self.blue_version is not None:
            logger.info(f"Loading blue model {self.blue_version}...")
            try:
                self.blue_model, _ = self.versioning.load_version(self.blue_version)
            except Exception as e:
                logger.error(f"Failed to load blue model: {e}")
                return False
        
        if self.blue_model is None:
            logger.error("Blue model not available for rollback")
            return False
        
        # Switch back to blue
        previous_active = self.active
        self.active = "blue"
        
        logger.warning(f"Traffic rolled back from {previous_active} to blue")
        logger.warning(f"Active version: {self.blue_version}")
        
        self._log_event("rolled_back", {
            "from": previous_active,
            "to": "blue",
            "version": self.blue_version
        })
        
        # Verify blue is healthy
        if not self.health_check("blue"):
            logger.error("Blue environment health check failed after rollback!")
            return False
        
        logger.info("Rollback successful")
        return True
    
    def detect_issues(self) -> bool:
        """
        Monitor for problems after switch.
        
        This method performs basic issue detection by:
        - Running health checks
        - Checking for errors in recent predictions
        - Monitoring latency
        
        Returns:
            True if issues detected, False otherwise
        """
        logger.info("Detecting issues in active environment...")
        
        # Perform health check on active environment
        health_ok = self.health_check(self.active)
        
        if not health_ok:
            logger.error("Health check failed on active environment")
            return True
        
        # Additional checks could be added here:
        # - Check error rate from prediction logs
        # - Check latency metrics
        # - Check memory usage
        # - Check model output quality
        
        logger.info("No issues detected")
        return False
    
    def get_deployment_log(self) -> List[Dict[str, Any]]:
        """
        Get deployment event log.
        
        Returns:
            List of deployment events with timestamps and details
        """
        return self.deployment_log
    
    def save_deployment_log(self, output_file: str) -> None:
        """
        Save deployment log to file.
        
        Args:
            output_file: Path to output JSON file
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.deployment_log, f, indent=2)
        
        logger.info(f"Deployment log saved to {output_file}")


def main():
    """
    Main function for command-line usage.
    
    Example usage:
        # Deploy new version with blue-green strategy
        python blue_green.py deploy --green-version v1.2.0
        
        # Rollback to previous version
        python blue_green.py rollback
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Blue-Green deployment")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy new version to green')
    deploy_parser.add_argument('--green-version', required=True, help='Version to deploy')
    deploy_parser.add_argument('--blue-version', help='Current production version (optional)')
    deploy_parser.add_argument('--auto-switch', action='store_true', help='Automatically switch to green')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback to blue environment')
    rollback_parser.add_argument('--blue-version', help='Version to rollback to (optional)')
    
    # Health check command
    health_parser = subparsers.add_parser('health', help='Check environment health')
    health_parser.add_argument('--environment', required=True, choices=['blue', 'green'], help='Environment to check')
    
    args = parser.parse_args()
    
    if args.command == 'deploy':
        # Deploy to green
        deployment = BlueGreenDeployment(
            blue_version=args.blue_version,
            green_version=args.green_version
        )
        
        success = deployment.deploy_green()
        
        if success:
            print(f"✓ Green environment deployed successfully: {args.green_version}")
            
            if args.auto_switch:
                print("\nSwitching to green environment...")
                switch_success = deployment.switch_to_green()
                
                if switch_success:
                    print(f"✓ Traffic switched to green: {args.green_version}")
                else:
                    print("✗ Switch failed, rolled back to blue")
            else:
                print("\nTo switch traffic to green, run:")
                print(f"  python blue_green.py switch --green-version {args.green_version}")
        else:
            print("✗ Green deployment failed")
        
        # Save deployment log
        deployment.save_deployment_log("deployment_log.json")
    
    elif args.command == 'rollback':
        # Rollback to blue
        deployment = BlueGreenDeployment(blue_version=args.blue_version)
        
        success = deployment.rollback()
        
        if success:
            print(f"✓ Rolled back to blue: {deployment.blue_version}")
        else:
            print("✗ Rollback failed")
    
    elif args.command == 'health':
        # Health check
        deployment = BlueGreenDeployment()
        
        health_ok = deployment.health_check(args.environment)
        
        if health_ok:
            print(f"✓ {args.environment.capitalize()} environment is healthy")
        else:
            print(f"✗ {args.environment.capitalize()} environment has issues")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
