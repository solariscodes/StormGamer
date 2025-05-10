import os
import webbrowser
from app import app

if __name__ == "__main__":
    # Get the admin key
    admin_key = os.environ.get('ADMIN', 'stormgamer_admin_key')
    
    # Print the admin URL for easy access
    print("\n===== STORMGAMER ADMIN PANEL =====")
    print(f"Admin URL: http://localhost:5000/admin/panel?key={admin_key}")
    print("==================================\n")
    
    # Open the admin panel in the default browser
    webbrowser.open(f"http://localhost:5000/admin/panel?key={admin_key}")
    
    # Run the Flask app
    app.run(debug=True)
