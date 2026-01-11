"""
ClimateSense - Flask Backend Application
AI Climate Action & Carbon Footprint Reduction Agent
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid

# Import agents
from agents import (
    CarbonEstimator,
    ImpactAnalysisAgent,
    RecommendationAgent,
    ClimateChatAgent,
    ChallengeAgent
)

# Supabase
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex())
CORS(app)

# Initialize Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if supabase_url and supabase_key:
    supabase: Client = create_client(supabase_url, supabase_key)
else:
    supabase = None
    print("Warning: Supabase credentials not found. Database features will be disabled.")


@app.route('/')
def index():
    """Home page - username input"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    username = session.get('username', 'User')
    return render_template('dashboard.html', username=username)


@app.route('/api/register', methods=['POST'])
def register_user():
    """Register a new user"""
    data = request.json
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    try:
        # Check if user exists
        if supabase:
            existing = supabase.table('users').select('*').eq('username', username).execute()
            if existing.data:
                user_id = existing.data[0]['id']
            else:
                # Create new user
                result = supabase.table('users').insert({
                    'username': username,
                    'created_at': datetime.utcnow().isoformat()
                }).execute()
                user_id = result.data[0]['id'] if result.data else str(uuid.uuid4())
        else:
            user_id = str(uuid.uuid4())
        
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'username': username
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def handle_ai_exception(e):
    error_text = str(e).lower()

    if "quota" in error_text or "rate" in error_text or "429" in error_text:
        return jsonify({
            'success': False,
            'error': 'AI is temporarily busy. Please try again in a few seconds. "Go to New Assessment to reset in sometime."'
        }), 429

    return jsonify({
        'success': False,
        'error': 'Something went wrong while processing AI response.'
    }), 500


@app.route('/api/calculate-footprint', methods=['POST'])
def calculate_footprint():
    """Calculate carbon footprint"""
    if 'user_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401
    
    data = request.json
    user_inputs = data.get('inputs', {})
    
    try:
        estimator = CarbonEstimator()
        footprint_data = estimator.estimate_footprint(user_inputs)
        
        # Get footprint level
        level, level_desc = estimator.get_footprint_level(footprint_data['total_score'])
        footprint_data['level'] = level
        footprint_data['level_description'] = level_desc
        
        # Save to database
        if supabase:
            supabase.table('footprints').insert({
                'user_id': session['user_id'],
                'inputs': user_inputs,
                'total_score': footprint_data['total_score'],
                'level': level,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
        
        return jsonify({
            'success': True,
            'footprint': footprint_data,
            'disclaimer': estimator.get_disclaimer()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """AI-powered impact analysis"""
    if 'user_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401
    
    data = request.json
    footprint_data = data.get('footprint')
    
    if not footprint_data:
        return jsonify({'error': 'Footprint data required'}), 400
    
    try:
        analysis_agent = ImpactAnalysisAgent()
        analysis_text = analysis_agent.analyze(footprint_data)
        
        return jsonify({
            'success': True,
            'analysis': analysis_text
        })
    except Exception as e:
        return handle_ai_exception(e)


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get prioritized recommendations"""
    if 'user_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401
    
    data = request.json
    footprint_data = data.get('footprint')
    analysis_text = data.get('analysis')
    
    if not footprint_data or not analysis_text:
        return jsonify({'error': 'Footprint and analysis data required'}), 400
    
    try:
        rec_agent = RecommendationAgent()
        recommendations = rec_agent.prioritize_recommendations(footprint_data, analysis_text)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    except Exception as e:
        return handle_ai_exception(e)

@app.route('/api/challenge', methods=['POST'])
def get_challenge():
    """Get One-Change Challenge"""
    if 'user_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401
    
    data = request.json
    footprint_data = data.get('footprint')
    recommendations_text = data.get('recommendations')
    
    if not footprint_data or not recommendations_text:
        return jsonify({'error': 'Footprint and recommendations data required'}), 400
    
    try:
        challenge_agent = ChallengeAgent()
        challenge = challenge_agent.suggest_challenge(footprint_data, recommendations_text)
        
        # Save challenge to database
        if supabase:
            insert_response = supabase.table('challenges').insert({
            'user_id': session['user_id'],
            'challenge_data': challenge
            }).execute()
        print("INSERT RESPONSE:", insert_response)

        challenge_id = insert_response.data[0]['id']
        print("CHALLENGE ID SENT:", challenge_id)

        return jsonify({
             'success': True,
             'challenge': challenge,
             'challenge_id': challenge_id
         })
        
        print("INSERT ERROR:", insert_response.error)

    except Exception as e:
        return handle_ai_exception(e)

@app.route('/api/challenge/accept', methods=['POST'])
def accept_challenge():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json(force=True)
    print("ACCEPT JSON:", data)

    challenge_id = data.get('challenge_id')

    if not challenge_id:
        return jsonify({'error': 'Challenge ID missing'}), 400

    response = supabase.table('challenges') \
        .update({'accepted': True}) \
        .eq('id', challenge_id) \
        .execute()

    if not response.data:
        return jsonify({'error': 'Challenge not found'}), 404

    return jsonify({'success': True})


@app.route('/api/chat', methods=['POST'])
def chat():
    """Climate advisor chat"""
    if 'user_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401
    
    data = request.json
    message = data.get('message')
    footprint_profile = data.get('footprint_profile', {})
    chat_history = data.get('chat_history', [])
    current_challenge = data.get('current_challenge')
    
    if not message:
        return jsonify({'error': 'Message required'}), 400
    
    try:
        chat_agent = ClimateChatAgent()
        response = chat_agent.chat(
            message,
            footprint_profile,
            chat_history,
            current_challenge
        )
        
        # Save chat to database
        if supabase:
            supabase.table('chat_history').insert({
                'user_id': session['user_id'],
                'user_message': message,
                'assistant_response': response,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
        
        return jsonify({
            'success': True,
            'response': response
        })
    except Exception as e:
        return handle_ai_exception(e)




@app.route('/api/user-history', methods=['GET'])
def get_user_history():
    """Get user's historical data"""
    if 'user_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401
    
    try:
        if supabase:
            footprints = supabase.table('footprints').select('*').eq('user_id', session['user_id']).order('created_at', desc=True).limit(10).execute()
            challenges = supabase.table('challenges').select('*').eq('user_id', session['user_id']).order('created_at', desc=True).limit(5).execute()
            
            return jsonify({
                'success': True,
                'footprints': footprints.data if footprints.data else [],
                'challenges': challenges.data if challenges.data else []
            })
        else:
            return jsonify({
                'success': True,
                'footprints': [],
                'challenges': []
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500





@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    """Leaderboard based on accepted challenges"""
    try:
        if not supabase:
            return jsonify([])

        # Count accepted challenges per user
        response = supabase.rpc(
            "leaderboard_accepted_challenges"
        ).execute()

        return jsonify({
            "success": True,
            "leaderboard": response.data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
