import os
import webbrowser
from app import app

if __name__ == "__main__":
    # Get the admin key from environment variable
    admin_key = os.environ.get('ADMIN')
    
    # Require ADMIN environment variable
    if not admin_key:
        print("\n===== ERROR: ADMIN KEY NOT SET =====")
        print("Please set the ADMIN environment variable before running this script")
        print("Example: export ADMIN=your_secure_key_here")
        print("=================================\n")
        exit(1)
    
    # Print the admin URL for easy access
    print("\n===== STORMGAMER ADMIN PANEL =====")
    print(f"Admin URL: http://localhost:5000/admin/panel?key={admin_key}")
    print("==================================\n")
    
    # Open the admin panel in the default browser
    webbrowser.open(f"http://localhost:5000/admin/panel?key={admin_key}")
    
    # Run the Flask app
    app.run(debug=True)
