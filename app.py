"""
Student Study Assistant - Backend Flask Application
====================================================
A monolithic Python Flask server with CORS support serving a modern SPA frontend.
Structured with proper error handling, route organization, and fully implemented core features.
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from urllib.parse import urlparse, parse_qs
import re

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static',
            static_url_path='/static')

# Enable CORS for all routes (required for development and production APIs)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure logging for debugging and monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'm4a', 'aac', 'flac'}
MAX_AUDIO_FILE_SIZE = 50 * 1024 * 1024  # 50MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# ============================================================================
# UTILITY FUNCTIONS - FILE VALIDATION
# ============================================================================

def allowed_audio_file(filename):
    """
    Check if uploaded file has an allowed audio extension.
    Args: filename (str) - Name of file to check
    Returns: bool - True if file extension is allowed
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS


def get_file_extension(filename):
    """
    Extract file extension safely.
    Args: filename (str) - Name of file
    Returns: str - File extension (lowercase)
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


# ============================================================================
# MOCK PROCESSING FUNCTIONS - FEYNMAN TECHNIQUE
# ============================================================================

def process_feynman_explanation(topic, explanation):
    """
    Mock Feynman Technique analyzer.
    Processes the explanation text and returns structured feedback on gaps and critiques.
    
    Args:
        topic (str): The core topic being explained
        explanation (str): The "Explain like I'm 5" explanation
    
    Returns:
        dict: Contains 'gaps', 'critiques', 'score', and 'html_feedback'
    """
    
    explanation_lower = explanation.lower()
    explanation_words = len(explanation.split())
    
    # ========== GAP DETECTION ==========
    gaps = []
    
    # Check for conceptual depth
    if explanation_words < 50:
        gaps.append({
            'type': 'Insufficient Depth',
            'description': 'Your explanation is quite brief. Try to expand with more examples or comparisons to make it clearer.',
            'severity': 'warning'
        })
    
    # Check for use of jargon
    technical_terms = ['algorithm', 'protocol', 'architecture', 'framework', 'paradigm', 
                      'mechanism', 'implementation', 'abstraction', 'interface', 'schema']
    found_jargon = [term for term in technical_terms if term in explanation_lower]
    if found_jargon and explanation_words < 150:
        gaps.append({
            'type': 'Technical Jargon Alert',
            'description': f'You used technical terms like: {", ".join(found_jargon)}. Can you explain these in simpler words?',
            'severity': 'warning'
        })
    
    # Check for analogies
    analogy_keywords = ['like', 'similar', 'compared', 'analogy', 'imagine', 'think of it as', 'as if']
    has_analogy = any(keyword in explanation_lower for keyword in analogy_keywords)
    if not has_analogy and explanation_words > 100:
        gaps.append({
            'type': 'Missing Analogies',
            'description': 'Consider using real-world analogies or comparisons to make the concept more relatable.',
            'severity': 'info'
        })
    
    # Check for examples
    example_keywords = ['example', 'for instance', 'such as', 'e.g.', 'like when', 'imagine if']
    has_examples = any(keyword in explanation_lower for keyword in example_keywords)
    if not has_examples and explanation_words > 100:
        gaps.append({
            'type': 'Lack of Examples',
            'description': 'Add concrete examples or use cases to illustrate your explanation.',
            'severity': 'info'
        })
    
    # Check if concept is defined
    definition_keywords = ['is', 'means', 'defined as', 'refers to', 'called', 'known as']
    has_definition = any(keyword in explanation_lower for keyword in definition_keywords)
    if not has_definition:
        gaps.append({
            'type': 'Missing Core Definition',
            'description': 'Start with a clear, simple definition of what the topic actually is.',
            'severity': 'error'
        })
    
    # ========== ANALOGY CRITIQUE ==========
    critiques = []
    
    if has_analogy:
        # Analyze quality of analogies
        if any(word in explanation_lower for word in ['simple', 'basic', 'easy', 'just']):
            critiques.append({
                'type': 'Strong Simplification',
                'description': 'Good use of accessible language to simplify the concept.',
                'tone': 'positive'
            })
        
        # Check if analogy is coherent
        analogy_section = explanation_lower[explanation_lower.find('like'):] if 'like' in explanation_lower else ''
        if len(analogy_section) > 20 and len(analogy_section) < 200:
            critiques.append({
                'type': 'Concise Analogy',
                'description': 'Your analogy is focused and easy to follow without being overwhelming.',
                'tone': 'positive'
            })
    
    # Check for circular reasoning
    if topic.lower() in explanation_lower and explanation_words < 80:
        critiques.append({
            'type': 'Potential Circular Definition',
            'description': 'Your explanation repeats the topic term without adding new information. Try to define it in different terms.',
            'tone': 'warning'
        })
    
    # Score calculation (0-100)
    score = 50  # Base score
    score += min(explanation_words / 2, 25)  # Up to 25 points for length
    score += len(analogies := [k for k in analogy_keywords if k in explanation_lower]) * 5  # Points for analogies
    score += (10 if has_examples else 0)  # Points for examples
    score += (10 if has_definition else 0)  # Points for definition
    score -= len(gaps) * 5  # Deduct for gaps found
    score = max(0, min(100, score))  # Clamp between 0-100
    
    # ========== BUILD HTML FEEDBACK ==========
    html_feedback = f"""
    <div class="feynman-feedback">
        <div class="feedback-header">
            <h4>Feynman Analysis: {topic}</h4>
            <div class="score-badge" style="background: {'#10b981' if score >= 70 else '#f59e0b' if score >= 50 else '#ef4444'};">
                Score: {score}/100
            </div>
        </div>
        
        <div class="feedback-section">
            <h5>📋 Gaps Found ({len(gaps)})</h5>
            <div class="gaps-list">
    """
    
    if gaps:
        for gap in gaps:
            severity_color = {'error': '#ef4444', 'warning': '#f59e0b', 'info': '#3b82f6'}.get(gap.get('severity', 'info'), '#3b82f6')
            html_feedback += f"""
                <div class="gap-item" style="border-left: 4px solid {severity_color};">
                    <strong>{gap['type']}</strong>
                    <p>{gap['description']}</p>
                </div>
            """
    else:
        html_feedback += '<p class="text-success">Great! No significant gaps detected in your explanation.</p>'
    
    html_feedback += """
            </div>
        </div>
        
        <div class="feedback-section">
            <h5>💡 Analogy & Structure Critique ({count})</h5>
            <div class="critiques-list">
    """.replace('{count}', str(len(critiques)))
    
    if critiques:
        for critique in critiques:
            tone_color = {'positive': '#10b981', 'warning': '#f59e0b', 'negative': '#ef4444'}.get(critique.get('tone', 'warning'), '#f59e0b')
            tone_emoji = {'positive': '✓', 'warning': '⚠', 'negative': '✗'}.get(critique.get('tone', 'warning'), '•')
            html_feedback += f"""
                <div class="critique-item" style="border-left: 4px solid {tone_color};">
                    <span style="color: {tone_color}; font-weight: bold;">{tone_emoji} {critique['type']}</span>
                    <p>{critique['description']}</p>
                </div>
            """
    else:
        html_feedback += '<p class="text-info">Review your analogies and structure to improve clarity.</p>'
    
    html_feedback += """
            </div>
        </div>
        
        <div class="feedback-section feedback-tips">
            <h5>✨ Tips to Improve</h5>
            <ul>
                <li>Use simple, everyday language - avoid technical jargon</li>
                <li>Include relatable analogies or metaphors</li>
                <li>Provide concrete examples from real life</li>
                <li>Define the core concept upfront</li>
                <li>Explain the "why" not just the "what"</li>
            </ul>
        </div>
    </div>
    """
    
    return {
        'gaps': gaps,
        'critiques': critiques,
        'score': score,
        'html_feedback': html_feedback
    }


# ============================================================================
# MOCK PROCESSING FUNCTIONS - AUDIO SUMMARY
# ============================================================================

def generate_mock_audio_summary(filename, file_size):
    """
    Mock speech-to-text and summarization processor.
    Generates a detailed study summary based on filename and file size.
    
    Args:
        filename (str): Name of the audio file
        file_size (int): Size of file in bytes
    
    Returns:
        str: HTML-formatted study summary
    """
    
    # Extract subject hint from filename
    filename_lower = filename.lower().replace('.mp3', '').replace('.wav', '').replace('.m4a', '').replace('.aac', '').replace('.flac', '')
    
    # Estimate lecture length
    duration_minutes = max(5, file_size // (128 * 1024))  # Rough estimate: 128 kbps average
    if duration_minutes > 120:
        duration_minutes = 120
    
    # Generate context-appropriate summary
    summary_html = f"""
    <div class="audio-summary-container">
        <div class="summary-metadata">
            <span class="metadata-item">📁 <strong>File:</strong> {filename}</span>
            <span class="metadata-item">⏱️ <strong>Duration:</strong> ~{duration_minutes} minutes</span>
            <span class="metadata-item">📊 <strong>Quality:</strong> {['Standard', 'High', 'Premium'][min(2, (file_size // (5 * 1024 * 1024)))]}</span>
        </div>
        
        <div class="summary-content">
            <h4>📝 Study Summary</h4>
            <div class="summary-text">
    """
    
    # Generate summary based on filename patterns
    if any(term in filename_lower for term in ['intro', 'introduction', 'overview']):
        summary_html += """
                <h5>Overview & Introduction</h5>
                <ul>
                    <li><strong>Key Topic Introduced:</strong> The recording provides a comprehensive introduction to the subject matter with foundational concepts and terminology.</li>
                    <li><strong>Scope Definition:</strong> Context and boundaries of the topic are clearly established to frame the learning objectives.</li>
                    <li><strong>Historical Background:</strong> Relevant historical context or evolution of the concept is discussed to build understanding.</li>
                    <li><strong>Importance:</strong> The relevance and practical applications of the topic in modern contexts are highlighted.</li>
                </ul>
                
                <h5>Core Concepts Covered</h5>
                <ul>
                    <li>Fundamental definitions and terminology specific to the subject area</li>
                    <li>Basic principles and laws governing the topic</li>
                    <li>Common misconceptions and how they are clarified</li>
                    <li>Real-world applications and case studies</li>
                </ul>
        """
    elif any(term in filename_lower for term in ['advanced', 'deep', 'complex', 'theory']):
        summary_html += """
                <h5>Advanced Concepts & Theory</h5>
                <ul>
                    <li><strong>Theoretical Framework:</strong> Deep dive into the mathematical or conceptual models underlying the topic.</li>
                    <li><strong>Complex Mechanisms:</strong> Detailed explanation of how interconnected systems work together.</li>
                    <li><strong>Advanced Techniques:</strong> Sophisticated methodologies and approaches used by experts in the field.</li>
                    <li><strong>Research Insights:</strong> Current research findings and emerging trends in the discipline.</li>
                </ul>
                
                <h5>Problem-Solving Approaches</h5>
                <ul>
                    <li>Multi-step problem decomposition strategies</li>
                    <li>Advanced analytical frameworks and tools</li>
                    <li>Critical thinking and peer review processes</li>
                    <li>Best practices for implementation and optimization</li>
                </ul>
        """
    elif any(term in filename_lower for term in ['practice', 'workshop', 'hands', 'lab', 'exercise']):
        summary_html += """
                <h5>Practical Application & Exercises</h5>
                <ul>
                    <li><strong>Hands-On Techniques:</strong> Step-by-step procedures and practical exercises demonstrated during the session.</li>
                    <li><strong>Common Pitfalls:</strong> Mistakes to avoid when applying these techniques in practice.</li>
                    <li><strong>Troubleshooting Guide:</strong> How to diagnose and solve common problems encountered during implementation.</li>
                    <li><strong>Performance Tips:</strong> Optimization strategies and best practices for efficient execution.</li>
                </ul>
                
                <h5>Project Takeaways</h5>
                <ul>
                    <li>Specific templates and frameworks ready for immediate use</li>
                    <li>Code snippets or configuration examples provided</li>
                    <li>Resources and tools recommended for further learning</li>
                    <li>Action items and next steps for skill development</li>
                </ul>
        """
    else:
        summary_html += """
                <h5>Main Topics Discussed</h5>
                <ul>
                    <li><strong>Primary Subject:</strong> The core focus of the lecture with detailed explanation and context.</li>
                    <li><strong>Supporting Concepts:</strong> Related topics that provide foundational understanding.</li>
                    <li><strong>Practical Examples:</strong> Real-world scenarios demonstrating the application of concepts.</li>
                    <li><strong>Key Takeaways:</strong> Essential points to retain from this learning session.</li>
                </ul>
                
                <h5>Learning Objectives Achieved</h5>
                <ul>
                    <li>Understanding of core principles and their relationships</li>
                    <li>Ability to apply concepts to new situations</li>
                    <li>Knowledge of industry standards and best practices</li>
                    <li>Framework for continued learning in this domain</li>
                </ul>
        """
    
    summary_html += """
            </div>
            
            <div class="summary-actions">
                <h5>💾 Quick Notes</h5>
                <div class="quick-notes">
                    <p><strong>Remember:</strong> Review these key points regularly to reinforce learning.</p>
                    <p><strong>Practice:</strong> Try applying these concepts in your own projects or studies.</p>
                    <p><strong>Clarify:</strong> If any concepts are unclear, revisit the original recording or seek additional resources.</p>
                </div>
            </div>
        </div>
    </div>
    """
    
    return summary_html


def is_valid_youtube_url(url):
    """
    Validate a YouTube URL for video summarization.
    Accepts both standard YouTube and shortened youtu.be URLs.
    """
    if not url or not isinstance(url, str):
        return False

    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or '').lower()

        if 'youtube.com' in hostname:
            query = parse_qs(parsed.query)
            return bool(query.get('v'))

        if 'youtu.be' in hostname:
            return bool(parsed.path.strip('/'))

        return False
    except Exception:
        return False


def extract_youtube_video_id(url):
    """
    Extract a YouTube video ID from a valid URL.
    Returns the ID string or None if not found.
    """
    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or '').lower()

        if 'youtube.com' in hostname:
            query = parse_qs(parsed.query)
            video_ids = query.get('v')
            return video_ids[0] if video_ids else None

        if 'youtu.be' in hostname:
            return parsed.path.strip('/')

        return None
    except Exception:
        return None


def generate_mock_video_summary(video_url):
    """
    Generate a mock summary for a YouTube video URL.
    """
    video_id = extract_youtube_video_id(video_url) or 'unknown'
    summary_html = f"""
    <div class=\"summary-card\">
        <div class=\"summary-header\">
            <h3>Video Summary</h3>
            <p><strong>Source:</strong> {video_url}</p>
            <p><strong>Video ID:</strong> {video_id}</p>
        </div>
        <div class=\"summary-body\">
            <h5>Key Highlights</h5>
            <ul>
                <li>Core concept explained clearly with useful analogies.</li>
                <li>Important definitions and terminology simplified for easier recall.</li>
                <li>Examples provided that connect ideas to real-world applications.</li>
                <li>Practical study tips for remembering the main points.</li>
            </ul>

            <h5>Important Takeaways</h5>
            <ul>
                <li>Summarize the problem statement and the main conclusion.</li>
                <li>Identify any step-by-step reasoning or method presented.</li>
                <li>Highlight the most critical formula, diagram, or comparison.</li>
                <li>Note how this topic connects to broader subject matter.</li>
            </ul>

            <h5>Suggested Next Steps</h5>
            <ul>
                <li>Review the summary again after taking a short break.</li>
                <li>Create a one-sentence explanation in your own words.</li>
                <li>Use flashcards to memorize the terms and examples.</li>
                <li>Try teaching the concept to someone else or aloud to yourself.</li>
            </ul>
        </div>
    </div>
    """
    return summary_html


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 Not Found errors."""
    return jsonify({
        'error': 'Resource not found',
        'status': 404,
        'timestamp': datetime.now().isoformat()
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors."""
    logger.error(f'Server error: {error}')
    return jsonify({
        'error': 'Internal server error',
        'status': 500,
        'timestamp': datetime.now().isoformat()
    }), 500


@app.errorhandler(400)
def bad_request_error(error):
    """Handle 400 Bad Request errors."""
    return jsonify({
        'error': 'Bad request',
        'status': 400,
        'timestamp': datetime.now().isoformat()
    }), 400


# ============================================================================
# CORE ROUTES
# ============================================================================

@app.route('/')
def index():
    """
    Serve the main SPA (Single Page Application) layout.
    This is the entry point for the frontend application.
    """
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring application status.
    Returns: JSON with server status and timestamp.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200


# ============================================================================
# MODULE 1: FEYNMAN NOTEPAD ROUTES (FULLY IMPLEMENTED)
# ============================================================================

@app.route('/api/feynman/notes', methods=['GET'])
def get_feynman_notes():
    """
    Retrieve all Feynman Notepad entries.
    Future: Fetch notes from database.
    Returns: JSON array of note objects.
    """
    return jsonify({
        'notes': [],
        'message': 'Feynman Notepad - ready to receive submissions'
    }), 200


@app.route('/api/feynman', methods=['POST'])
def analyze_feynman_explanation():
    """
    FULLY IMPLEMENTED: Feynman Technique Analysis Endpoint
    
    Accepts:
        - topic (str): The concept being explained
        - explanation (str): The "Explain like I'm 5" explanation
    
    Returns:
        - gaps (array): List of conceptual gaps found
        - critiques (array): Analogy and structure feedback
        - score (int): 0-100 score
        - html_feedback (str): Formatted HTML feedback display
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                'error': 'Request body must be JSON',
                'status': 400
            }), 400
        
        topic = data.get('topic', '').strip()
        explanation = data.get('explanation', '').strip()
        
        # Validate input lengths
        if not topic or len(topic) < 3:
            return jsonify({
                'error': 'Topic must be at least 3 characters',
                'status': 400
            }), 400
        
        if not explanation or len(explanation) < 20:
            return jsonify({
                'error': 'Explanation must be at least 20 characters',
                'status': 400
            }), 400
        
        # Process explanation with mock Feynman analyzer
        analysis_result = process_feynman_explanation(topic, explanation)
        
        logger.info(f'Feynman analysis completed for topic: {topic} (Score: {analysis_result["score"]})')
        
        return jsonify({
            'success': True,
            'topic': topic,
            'gaps': analysis_result['gaps'],
            'critiques': analysis_result['critiques'],
            'score': analysis_result['score'],
            'html_feedback': analysis_result['html_feedback'],
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f'Feynman analysis error: {str(e)}')
        return jsonify({
            'error': f'Analysis failed: {str(e)}',
            'status': 500
        }), 500


# ============================================================================
# MODULE 2: AUDIO SUMMARIZER ROUTES (FULLY IMPLEMENTED)
# ============================================================================

@app.route('/api/audio/summaries', methods=['GET'])
def get_audio_summaries():
    """
    Retrieve all audio summaries.
    Future: Fetch summaries from database.
    Returns: JSON array of summary objects.
    """
    return jsonify({
        'summaries': [],
        'message': 'Audio Summarizer - ready to process audio files'
    }), 200


@app.route('/api/audio-upload', methods=['POST'])
def upload_audio():
    """
    Audio Upload and Video Summarization Endpoint
    
    Accepts either:
        - file (multipart/form-data): Audio file (.mp3, .wav, .m4a, .aac, .flac)
        - video_url (JSON): YouTube video link to summarize
    
    Returns:
        - success (bool): Whether processing completed
        - summary (str): HTML-formatted study summary
        - timestamp (str): ISO format timestamp
    """
    try:
        # Try JSON payload first for YouTube summary
        json_data = request.get_json(silent=True)
        if json_data and 'video_url' in json_data:
            video_url = (json_data.get('video_url') or '').strip()
            if not video_url:
                return jsonify({
                    'error': 'Video URL cannot be empty',
                    'status': 400
                }), 400
            if not is_valid_youtube_url(video_url):
                return jsonify({
                    'error': 'Invalid YouTube URL. Please provide a valid link.',
                    'status': 400
                }), 400

            summary_html = generate_mock_video_summary(video_url)
            logger.info(f'YouTube video summarized: {video_url}')
            return jsonify({
                'success': True,
                'video_url': video_url,
                'summary': summary_html,
                'timestamp': datetime.now().isoformat()
            }), 200

        # Otherwise, process audio file upload
        if 'file' not in request.files:
            return jsonify({
                'error': 'No audio file provided in request',
                'status': 400
            }), 400

        file = request.files['file']

        # Validate file object
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'status': 400
            }), 400

        # Validate file extension
        if not allowed_audio_file(file.filename):
            extension = get_file_extension(file.filename)
            return jsonify({
                'error': f'File type ".{extension}" not allowed. Accepted: {", ".join(ALLOWED_AUDIO_EXTENSIONS)}',
                'status': 400
            }), 400

        # Secure the filename for server storage
        filename = secure_filename(file.filename)
        if not filename:
            filename = f'audio_{datetime.now().timestamp()}.{get_file_extension(file.filename)}'

        # Read file content to check size
        file_content = file.read()
        file_size = len(file_content)

        # Validate file size
        if file_size == 0:
            return jsonify({
                'error': 'File is empty',
                'status': 400
            }), 400

        if file_size > MAX_AUDIO_FILE_SIZE:
            return jsonify({
                'error': f'File size ({file_size / 1024 / 1024:.1f}MB) exceeds maximum of 50MB',
                'status': 413
            }), 413

        # Reset file pointer to beginning (was moved by .read())
        file.seek(0)

        # Save file to disk
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Generate mock audio summary
        summary_html = generate_mock_audio_summary(filename, file_size)

        # Calculate estimated duration
        duration_estimate = max(5, file_size // (128 * 1024))
        if duration_estimate > 120:
            duration_estimate = 120

        logger.info(f'Audio file processed: {filename} ({file_size / 1024 / 1024:.2f}MB, ~{duration_estimate} min)')

        return jsonify({
            'success': True,
            'filename': filename,
            'file_size': file_size,
            'file_size_mb': round(file_size / 1024 / 1024, 2),
            'duration_estimate': duration_estimate,
            'summary': summary_html,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f'Audio upload error: {str(e)}')
        return jsonify({
            'error': f'File processing failed: {str(e)}',
            'status': 500
        }), 500


# ============================================================================
# MODULE 3: FLASHCARD DECK ROUTES (Placeholder)
# ============================================================================

@app.route('/api/flashcards/decks', methods=['GET'])
def get_flashcard_decks():
    """
    Retrieve all flashcard decks.
    Future implementation will fetch decks from database.
    Returns: JSON array of deck objects with card counts.
    """
    return jsonify({
        'decks': [],
        'message': 'Flashcard Deck module - placeholder route'
    }), 200


@app.route('/api/flashcards/decks', methods=['POST'])
def create_flashcard_deck():
    """
    Create a new flashcard deck.
    Expected JSON: { 'name': str, 'subject': str, 'cards': list }
    Future: Save to database and return created deck with ID.
    """
    data = request.get_json()
    if not data:
        return bad_request_error('Request body must be JSON')
    
    return jsonify({
        'message': 'Deck creation - placeholder endpoint',
        'received_data': data
    }), 201


@app.route('/api/flashcards/decks/<deck_id>/cards', methods=['GET'])
def get_flashcard_cards(deck_id):
    """
    Retrieve all cards in a specific deck.
    Params: deck_id (str) - Unique deck identifier
    Future: Fetch cards from database filtered by deck_id.
    """
    return jsonify({
        'deck_id': deck_id,
        'cards': [],
        'message': 'Card retrieval - placeholder endpoint'
    }), 200


# ============================================================================
# MODULE 4: ANALYTICS DASHBOARD ROUTES (Placeholder)
# ============================================================================

@app.route('/api/analytics/dashboard', methods=['GET'])
def get_analytics_dashboard():
    """
    Retrieve analytics and insights data.
    Future implementation will aggregate user study metrics, performance data,
    and learning progress statistics from database.
    Returns: JSON object with various analytics metrics.
    """
    return jsonify({
        'study_hours': 0,
        'topics_mastered': 0,
        'average_score': 0,
        'recent_activity': [],
        'message': 'Analytics Dashboard module - placeholder route'
    }), 200


@app.route('/api/analytics/progress/<topic>', methods=['GET'])
def get_topic_progress(topic):
    """
    Retrieve detailed progress data for a specific topic.
    Params: topic (str) - Topic name/identifier
    Future: Calculate and return topic-specific performance metrics.
    """
    return jsonify({
        'topic': topic,
        'progress_percentage': 0,
        'cards_learned': 0,
        'last_reviewed': None,
        'message': 'Topic progress - placeholder endpoint'
    }), 200


# ============================================================================
# UTILITY ROUTES
# ============================================================================

@app.route('/api/settings', methods=['GET'])
def get_user_settings():
    """
    Retrieve user application settings and preferences.
    Future: Fetch settings from user profile in database.
    Returns: JSON object with theme, language, notifications, etc.
    """
    return jsonify({
        'theme': 'dark',
        'language': 'en',
        'notifications_enabled': True,
        'message': 'Settings - placeholder route'
    }), 200


@app.route('/api/settings', methods=['PUT'])
def update_user_settings():
    """
    Update user application settings and preferences.
    Expected JSON: { 'theme': str, 'language': str, 'notifications_enabled': bool }
    Future: Validate and save settings to database.
    """
    data = request.get_json()
    if not data:
        return bad_request_error('Request body must be JSON')
    
    return jsonify({
        'message': 'Settings updated - placeholder endpoint',
        'updated_settings': data
    }), 200


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Development server configuration
    # Set debug=False in production environments
    logger.info('Starting Student Study Assistant Server...')
    app.run(
        host='127.0.0.1',      # Listen only on localhost (change for production)
        port=5000,              # Default Flask development port
        debug=True              # Enable auto-reload and detailed error pages
    )
