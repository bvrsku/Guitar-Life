#!/usr/bin/env python3
"""
Simple launcher for Guitar Life with HUD check
"""

try:
    print("Starting Guitar Life...")
    
    # Import main function
    from guitar_li4fe import main
    
    print("Import successful")
    
    # Run application
    main()
    
except KeyboardInterrupt:
    print("Application stopped by user")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()