#!/usr/bin/env python3
"""
Debug script to visualize the polling data flow in switchmap-ng
Shows how the system polls devices step by step
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, '/home/abhishek/files/gsoc/switchmap-ng')

# Import the polling module
from switchmap.poller import poll

def main():
    print("=" * 80)
    print("🚀 SWITCHMAP-NG POLLING FLOW DEBUGGER")
    print("=" * 80)
    print()
    
    # This will show the complete flow with our debug prints
    # Note: Make sure you have a valid configuration with at least one host
    try:
        # Use cli_device to poll a single device for debugging
        # Using one of the actual configured hostnames
        hostname = "162.249.37.218"  # One of the configured Cisco lab devices
        print(f"🎯 Starting debug poll for hostname: {hostname}")
        poll.cli_device(hostname)
        
    except Exception as e:
        print(f"❌ Error during polling: {e}")
        print()
        print("💡 To use this debugger:")
        print("1. Make sure you have a valid switchmap configuration")
        print("2. Update the hostname variable to match a device in your config")
        print("3. Ensure SNMP credentials are configured")
        print("4. Check network connectivity to the device")
        print()
        return
    
    print()
    print("=" * 80)
    print("✅ DEBUG POLLING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main() 