import os
import webbrowser
from app import create_app

app = create_app()

if __name__ == '__main__':
    is_production = (
        os.environ.get('FLASK_ENV', '').strip().lower() == 'production' or
        os.environ.get('ENV', '').strip().lower() == 'production' or
        os.environ.get('ENVIRONMENT', '').strip().lower() == 'production'
    )
    debug_mode = (
        not is_production and
        os.environ.get('FLASK_DEBUG', os.environ.get('DEBUG', 'false')).lower() in ('true', '1', 't')
    )

    # Automatically open web browser to the app home page
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        webbrowser.open('http://127.0.0.1:5000')
        
    # Ensure application starts locally on port 5000 and is accessible on the local network
    app.run(host='0.0.0.0', port=5000, debug=debug_mode, use_reloader=False)
