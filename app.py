import os
import webbrowser
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Automatically open web browser to the app home page
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        webbrowser.open('http://127.0.0.1:5000')
        
    # Ensure application starts locally on port 5000 and is accessible on the local network
    app.run(host='0.0.0.0', port=5000, debug=True)
