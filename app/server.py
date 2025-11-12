from flask import Flask, request, jsonify
from main import lambda_handler
import os
import ssl
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get configuration from environment variables
PLATFORM = os.getenv('PLATFORM', 'self-hosted').lower()
BOT_PORT = int(os.getenv('BOT_PORT', '8443'))
CERT_PATH = os.getenv('CERT_PATH', '/etc/letsencrypt/live/your-domain.com')

@app.route('/interactions', methods=['POST'])
def interactions():
    """Handle Discord bot interactions"""
    try:
        logger.info("Received interaction request")

        # Convert Flask request to Lambda-like event format
        event = {
            'body': request.get_data(as_text=True),
            'headers': {
                'x-signature-ed25519': request.headers.get('x-signature-ed25519'),
                'x-signature-timestamp': request.headers.get('x-signature-timestamp')
            }
        }

        # Call the existing Lambda handler
        response = lambda_handler(event, None)

        # lambda_handler returns a dict that looks like build_response output
        # It may already be a Flask/WSGI-friendly tuple; try to normalize
        if isinstance(response, dict):
            status = response.get('statusCode', 200)
            body = response.get('body', response)
            # If body is a dict or list, jsonify it
            if isinstance(body, (dict, list)):
                return jsonify(body), status
            # If body is a string, return as-is
            return (body, status)

        # Otherwise return whatever was returned
        return response

    except Exception as e:
        logger.exception("Error processing interaction")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'platform': PLATFORM,
        'port': BOT_PORT
    }), 200


def run_self_hosted():
    """Run as self-hosted HTTPS server"""
    try:
        # Create SSL context
        logger.info(f"Loading SSL certificates from {CERT_PATH}")
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(
            f'{CERT_PATH}/fullchain.pem',
            f'{CERT_PATH}/privkey.pem'
        )

        # Start Flask server with HTTPS
        logger.info(f"Starting bot as SELF-HOSTED on 0.0.0.0:{BOT_PORT}")
        app.run(
            host='0.0.0.0',
            port=BOT_PORT,
            ssl_context=ssl_context,
            debug=False,
            use_reloader=False
        )
    except FileNotFoundError as e:
        logger.error(f"SSL certificate files not found: {e}")
        logger.error(f"Expected path: {CERT_PATH}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Failed to start self-hosted server")
        sys.exit(1)


def run_lambda():
    """Run as AWS Lambda - returns lambda_handler function"""
    logger.info("Initializing for AWS LAMBDA deployment")
    logger.info("This server.py should not be executed in Lambda environment")
    logger.info("Use the lambda_handler from main.py instead")
    return lambda_handler


def main():
    """Entry point - platform selection"""
    if PLATFORM == 'lambda':
        logger.warning("Lambda mode detected but running via server.py")
        logger.warning("For Lambda, use the lambda_handler from main.py directly")
        sys.exit(1)
    elif PLATFORM in ['self-hosted', 'selfhosted', 'localhost']:
        run_self_hosted()
    else:
        logger.error(f"Unknown PLATFORM: {PLATFORM}")
        logger.error("Valid options: 'lambda', 'self-hosted'")
        sys.exit(1)


if __name__ == '__main__':
    main()
