#!/usr/bin/env python3
"""
Script to show what hostnames are actually configured in switchmap-ng
This will help you identify the correct hostname to use in debug_polling_flow.py
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, '/home/abhishek/files/gsoc/switchmap-ng')

try:
    from switchmap.poller.configuration import ConfigPoller
    
    def main():
        print("=" * 80)
        print("🔍 SWITCHMAP-NG CONFIGURED HOSTNAMES")
        print("=" * 80)
        print()
        
        try:
            # Get configuration
            config = ConfigPoller()
            
            # Get zones and their hostnames
            zones = config.zones()
            
            if not zones:
                print("❌ No zones configured!")
                print()
                print("💡 You need to configure zones and hostnames in your switchmap configuration file.")
                print("   Look for a file like config.yaml or switchmap.yaml in your installation.")
                return
            
            print(f"📋 Found {len(zones)} configured zone(s):")
            print()
            
            all_hostnames = []
            
            for i, zone in enumerate(zones, 1):
                print(f"🌍 Zone {i}: '{zone.name}'")
                if zone.hostnames and len(zone.hostnames) > 0:
                    print(f"   📍 Hostnames ({len(zone.hostnames)}):")
                    for hostname in zone.hostnames:
                        print(f"      - {hostname}")
                        all_hostnames.append(hostname)
                else:
                    print("   ❌ No hostnames configured in this zone")
                print()
            
            if all_hostnames:
                print("=" * 80)
                print("🎯 AVAILABLE HOSTNAMES FOR TESTING:")
                print("=" * 80)
                for hostname in all_hostnames:
                    print(f"   ✅ {hostname}")
                print()
                print("💡 To test the polling flow, update debug_polling_flow.py:")
                print(f"   Change hostname = \"localhost\" to hostname = \"{all_hostnames[0]}\"")
                print()
                print("🚀 Then run: python3 debug_polling_flow.py")
            else:
                print("❌ No hostnames found in any zone!")
                
        except Exception as e:
            print(f"❌ Error reading configuration: {e}")
            print()
            print("💡 This usually means:")
            print("1. Configuration file not found or invalid")
            print("2. Missing or incorrect configuration sections")
            print("3. Configuration file format issues")
            print()
            print("🔧 Check if you have a valid configuration file with:")
            print("   - core: section")
            print("   - poller: section")
            print("   - zones: with hostnames")
            
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print()
    print("💡 Make sure you're running this from the switchmap-ng root directory")
    print("   and that the switchmap package is properly installed.") 