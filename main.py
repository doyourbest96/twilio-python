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
twilio_numbers = ["+17372653760", "+18582992629"]

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://regular-tahr-artistic.ngrok-free.app",
            "https://central-lioness-hopefully.ngrok-free.app"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Accept", "Content-Type"],
        "supports_credentials": True
    }
})

@app.route('/', methods=['GET'])
def home():
    return render_template(
        'home.html',
        title="In-browser calls with Twilio",
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
    caller = request.form['Caller']

    print(request.form['From'] + ' --> ' + request.form['To'])

    if 'To' in request.form and request.form['To'] in twilio_numbers:
        print('incoming call')
        # Start recording the incoming call
        response.say("This call is being recorded.")
        response.record(action='/handle_recording', max_length=60)

        dial = Dial(callerId=caller)
        dial.client(request.form['To'].replace('+', ''))
        response.append(dial)
    else:
        print('outbound call')
        caller = request.form['From'].replace('client:', '+')
        # Start recording the outgoing call
        response.say("This call is being recorded.")
        response.record(action='/handle_outgoing_recording', max_length=60)

        dial = Dial(callerId=caller)
        dial.number(request.form['To'])
        response.append(dial)

    return str(response)

@app.route('/handle_recording', methods=['POST'])
def handle_recording():
    recording_url = request.form['RecordingUrl']
    print(f"Incoming call recording available at: {recording_url}")

    # Save the recording URL or process it as needed
    return "Recording received", 200

@app.route('/handle_outgoing_recording', methods=['POST'])
def handle_outgoing_recording():
    recording_url = request.form['RecordingUrl']
    print(f"Outgoing call recording available at: {recording_url}")

    # Save the recording URL or process it as needed
    return "Recording received", 200

if __name__ == "__main__":
    run_simple('localhost', 5000, app)
