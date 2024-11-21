from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask import request
 
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial
 
from werkzeug.serving import run_simple
from dotenv import load_dotenv
import os
import pprint as p

load_dotenv()

account_sid = os.environ['TWILIO_ACCOUNT_SID']
api_key = os.environ['TWILIO_API_KEY_SID']
api_key_secret = os.environ['TWILIO_API_KEY_SECRET']
twiml_app_sid = os.environ['TWIML_APP_SID']
twilio_number = os.environ['TWILIO_NUMBER']

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Accept", "Content-Type"],
        "supports_credentials": True
    }
})

@app.route('/', methods=['GET'])
def home():
    return render_template(
        'home.html',
        title="In browser calls",
    )

@app.route('/token', methods=['GET'])
def get_token():
    identity = request.args.get('identity', 'user')
    
    # Create access token with credentials
    access_token = AccessToken(
        account_sid,
        api_key,
        api_key_secret,
        identity=identity
    )

    # Create a Voice grant and add it to the token
    voice_grant = VoiceGrant(
        outgoing_application_sid=twiml_app_sid,
        incoming_allow=True
    )
    access_token.add_grant(voice_grant)

    # Generate the token
    return jsonify({
        'token': access_token.to_jwt(),
        'identity': identity
    })

@app.route('/handle_calls', methods=['POST'])
def call():
    p.pprint(request.form)
    response = VoiceResponse()
    dial = Dial(callerId=twilio_number)

    if 'To' in request.form and request.form['To'] != twilio_number:
        print('outbound call')
        dial.number(request.form['To'])
    else:
        print('incoming call')
        caller = request.form['Caller']
        dial = Dial(callerId=caller)
        dial.client(twilio_number)

    return str(response.append(dial))

if __name__ == "__main__":
    run_simple('localhost', 5000, app)