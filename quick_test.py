#!/usr/bin/env python3
"""
Quick test to verify time tracking is working end-to-end
"""

from moduller.active_window_tracker import start_active_window_tracking, get_current_activity_summary
from moduller.program_usage_aggregator import get_short_program_summary
import time

def quick_test():
    print('🔍 Quick test of time tracking accuracy...')
    
    # Start active window tracking
    print('▶️ Starting active window tracker...')
    start_active_window_tracking()
    
    # Wait a bit for tracker to initialize
    time.sleep(2)
    
    print('⏳ Tracking for 10 seconds, keep using VS Code...')
    
    # Track for 10 seconds
    for i in range(10):
        time.sleep(1)
        if i % 3 == 2:  # Every 3 seconds
            summary = get_current_activity_summary()
            apps = summary.get('applications', [])
            if apps:
                top_app = apps[0]
                print(f'📊 {i+1}s: {top_app["process_name"]} = {top_app["total_time_formatted"]}')
            else:
                print(f'📊 {i+1}s: No apps tracked yet')
    
    print('\n📋 Final aggregated summary:')
    final = get_short_program_summary()
    for program in final.get('programs', [])[:3]:
        print(f'  {program["program"]}: {program["time_formatted"]}')
    
    print(f'\nTotal time tracked: {final.get("total_tracked_time_formatted", "0s")}')
    
    # Check if time looks reasonable
    if final.get('total_tracked_time_seconds', 0) >= 8:
        print('✅ Time tracking appears to be working correctly!')
    else:
        print('⚠️ Time tracking might not be accumulating correctly')

if __name__ == "__main__":
    quick_test()
