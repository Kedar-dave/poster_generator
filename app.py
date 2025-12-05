from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import requests
import os
import hashlib
import json
from dotenv import load_dotenv

load_dotenv()

from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(hours=1)

# API URLs
USER_API_URL = os.getenv("USER_API_URL", "https://bgwp6whvle.execute-api.us-east-1.amazonaws.com/dev/user")
# Base URL for the poster/history API (from user screenshot/info)
POSTER_API_BASE = os.getenv("POSTER_API_BASE", "https://kiqi41dlld.execute-api.us-east-1.amazonaws.com/dev")

# Helper to hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('email')
        password = request.form.get('password')
        
        # Verify user against API
        try:
            print(f"Attempting login for {user_id}")
            response = requests.get(f"{USER_API_URL}", params={'user_id': user_id})
            print(f"API Response Status: {response.status_code}")
            print(f"API Response Body: {response.text}")
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Check for Lambda/API Gateway errors that return 200 OK
                # The API returns a structure like {"statusCode": 200, "body": "{\"key\": \"value\"}"}
                # We need to parse the inner 'body' string if it exists.
                if 'body' in user_data and isinstance(user_data['body'], str):
                    try:
                        inner_body = json.loads(user_data['body'])
                        user_data = inner_body
                    except json.JSONDecodeError:
                        print("Failed to parse inner JSON body")

                if 'errorMessage' in user_data or 'error' in user_data:
                    error_msg = user_data.get('errorMessage') or user_data.get('error')
                    flash(f'Login failed: {error_msg}')
                    print(f"API Error: {error_msg}")
                else:
                    stored_hash = user_data.get('password')
                    computed_hash = hash_password(password)
                    print(f"Stored Hash: {stored_hash}")
                    print(f"Computed Hash: {computed_hash}")
                    
                    if stored_hash == computed_hash:
                        session['user_id'] = user_id
                        session.permanent = True
                        response = redirect(url_for('dashboard'))
                        response.set_cookie('was_logged_in', 'true', max_age=3600)
                        return response
                    else:
                        flash('Invalid password')
                        print("Password mismatch")
            else:
                flash('User not found')
                print("User not found in API")
        except Exception as e:
            flash(f'Error logging in: {str(e)}')
            print(f"Login Exception: {e}")
            
    # Check if session expired (cookie exists but session is empty)
    if 'user_id' not in session and request.cookies.get('was_logged_in'):
        flash('Session expired. Please login again.')
        response = make_response(render_template('login.html'))
        response.delete_cookie('was_logged_in')
        return response

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_id = request.form.get('email')
        password = request.form.get('password')
        hashed_pw = hash_password(password)
        
        try:
            # POST /user with user_id and password
            # DEBUG: Try sending raw password if server hashes it, or hashed if it doesn't.
            # Currently sending HASHED password.
            payload = {"user_id": user_id, "password": hashed_pw}
            print(f"Signing up user: {user_id} with payload: {payload}")
            
            response = requests.post(USER_API_URL, json=payload)
            print(f"Signup Response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                resp_json = response.json()
                if 'errorMessage' in resp_json or 'error' in resp_json:
                    error_msg = resp_json.get('errorMessage') or resp_json.get('error')
                    flash(f'Signup failed: {error_msg}')
                else:
                    flash('Signup successful! Please login.')
                    return redirect(url_for('login'))
            else:
                flash('Error creating account')
        except Exception as e:
            flash(f'Error signing up: {str(e)}')
            print(f"Signup Exception: {e}")

    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    posters = []
    
    try:
        # GET /history?user_id=<id>
        history_endpoint = f"{POSTER_API_BASE}/history"
        print(f"Fetching history from: {history_endpoint}")
        response = requests.get(history_endpoint, params={'user_id': user_id})
        print(f"History API Status: {response.status_code}")
        print(f"History API Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Handle nested body if present (API Gateway/Lambda common pattern)
            if isinstance(data, dict) and 'body' in data:
                try:
                    if isinstance(data['body'], str):
                        posters = json.loads(data['body'])
                    else:
                        posters = data['body']
                except json.JSONDecodeError:
                    print("Failed to parse history body")
                    posters = []
            else:
                posters = data
                
            # Handle case where posters is a list of strings (stringified JSONs)
            if isinstance(posters, list):
                parsed_posters = []
                for p in posters:
                    if isinstance(p, str):
                        try:
                            parsed_posters.append(json.loads(p))
                        except:
                            pass
                    else:
                        parsed_posters.append(p)
                posters = parsed_posters
                
            # Clean URLs (Fix for trailing backslash issue)
            if isinstance(posters, list):
                for p in posters:
                    if isinstance(p, dict) and 'poster_url' in p and p['poster_url']:
                        p['poster_url'] = p['poster_url'].strip('\\')
                        # Also fix if it's double quoted or has other artifacts
                        p['poster_url'] = p['poster_url'].strip('"')
                
    except Exception as e:
        flash(f"Error fetching history: {str(e)}")
        print(f"Dashboard Exception: {e}")
        
    return render_template('dashboard.html', posters=posters)

@app.route('/generate', methods=['POST'])
def generate():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    prompt = request.form.get('prompt')
    user_id = session['user_id']
    
    try:
        # GET /movie-poster-api-design (User confirmed it's GET)
        generate_endpoint = f"{POSTER_API_BASE}/movie-poster-api-design"
        params = {"user_id": user_id, "prompt": prompt}
        print(f"Generating poster at: {generate_endpoint}")
        print(f"Params: {params}")
        
        response = requests.get(generate_endpoint, params=params)
        print(f"Generate API Status: {response.status_code}")
        print(f"Generate API Body: {response.text}")
        
        if response.status_code != 200:
             flash(f"Generation failed: {response.text}")
        
        # We don't necessarily need to do anything with the response if we just reload the dashboard
        # The dashboard will fetch the new history.
    except Exception as e:
        flash(f"Error generating poster: {str(e)}")
        print(f"Generate Exception: {e}")
        
    return redirect(url_for('dashboard'))

@app.route('/unlock', methods=['POST'])
def unlock():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    prompt_used = request.form.get('prompt_used')
    user_id = session['user_id']
    
    try:
        # POST /pay
        set_paid_endpoint = f"{POSTER_API_BASE}/pay"
        payload = {"user_id": user_id, "prompt_used": prompt_used}
        print(f"Unlocking poster at: {set_paid_endpoint}")
        print(f"Payload: {payload}")
        
        response = requests.post(set_paid_endpoint, json=payload)
        print(f"Unlock API Status: {response.status_code}")
        print(f"Unlock API Body: {response.text}")
        
        if response.status_code != 200:
            flash(f"Unlock failed: {response.text}")
            
    except Exception as e:
        flash(f"Error unlocking poster: {str(e)}")
        print(f"Unlock Exception: {e}")
        
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    response = redirect(url_for('login'))
    response.delete_cookie('was_logged_in')
    return response

if __name__ == '__main__':
    app.run(debug=True)
