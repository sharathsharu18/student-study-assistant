# Student Study Assistant - Base Project Setup

## 📚 Project Overview

A modern Student Study Assistant web application built with:

- **Frontend**: Vanilla JavaScript SPA with semantic HTML5 and clean CSS3
- **Backend**: Python Flask with CORS support
- **Architecture**: Clean, scalable monolithic structure ready for phase-based development

## 🎯 Core Modules (Phase 1)

1. **Feynman Notepad** - Explain concepts in simple terms to deepen understanding
2. **Audio Summarizer** - Convert lectures and discussions into concise summaries
3. **Flashcard Deck** - Create and review flashcards for efficient memorization
4. **Analytics Dashboard** - Track learning progress and performance metrics

## 🏗️ Project Structure

```
nithin_intern_project/
├── app.py                    # Flask backend server
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── templates/
│   └── index.html           # Main SPA layout
└── static/
    └── style.css            # Global stylesheet
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation & Setup

1. **Navigate to project directory:**

   ```bash
   cd nithin_intern_project
   ```

2. **Create a Python virtual environment** (recommended):

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask development server:**

   ```bash
   python app.py
   ```

5. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

You should see the Student Study Assistant dashboard with all 4 module tabs ready!

## 📋 File Descriptions

### `app.py`

- **Purpose**: Flask backend server
- **Features**:
  - CORS enabled for all API routes
  - Comprehensive error handlers (400, 404, 500)
  - Health check endpoint for monitoring
  - Placeholder routes for all 4 core modules
  - Clean separation of concerns with documented sections
  - Production-ready logging

### `templates/index.html`

- **Purpose**: Main SPA layout
- **Features**:
  - Semantic HTML5 structure
  - Responsive sidebar navigation with 4 module tabs
  - Dynamic module switching with vanilla JavaScript
  - Theme toggle (dark/light mode)
  - Help button and settings panel
  - Modular vanilla JavaScript with async/await Fetch API
  - Zero external framework dependencies

### `static/style.css`

- **Purpose**: Global stylesheet
- **Features**:
  - Pure CSS3 with no frameworks (no Bootstrap/Tailwind)
  - CSS Variables for theming system
  - Dark/light theme support with smooth transitions
  - Responsive grid layout (desktop/tablet/mobile)
  - Modern slate color scheme
  - Flexbox-based flexible layouts
  - Accessibility features (focus states, reduced motion support)
  - Custom scrollbar styling

## 🔌 API Endpoints

### Health Check

- `GET /api/health` - Server status

### Feynman Notepad

- `GET /api/feynman/notes` - Retrieve all notes
- `POST /api/feynman/notes` - Create new note

### Audio Summarizer

- `GET /api/audio/summaries` - Retrieve summaries
- `POST /api/audio/upload` - Upload and process audio

### Flashcard Deck

- `GET /api/flashcards/decks` - Retrieve all decks
- `POST /api/flashcards/decks` - Create new deck
- `GET /api/flashcards/decks/<deck_id>/cards` - Get cards from deck

### Analytics Dashboard

- `GET /api/analytics/dashboard` - Get analytics data
- `GET /api/analytics/progress/<topic>` - Get topic progress

### Settings

- `GET /api/settings` - Retrieve user settings
- `PUT /api/settings` - Update user settings

## 🎨 Customization

### Theming

Users can toggle between dark and light themes using the moon/sun icon in the sidebar footer. Theme preference is persisted in localStorage.

### Color Scheme

Edit CSS variables in `static/style.css` (`:root` and `[data-theme="light"]` sections) to customize colors.

### Module Switching

Add new modules by:

1. Creating a new `<button class="nav-link" data-module="modulename">` in sidebar
2. Adding corresponding `<div class="module-view" id="modulename-view">` section
3. Updating the titles object in JavaScript
4. Creating backend routes in `app.py`

## 📱 Responsive Breakpoints

- **Desktop**: Full 2-column layout (sidebar + content)
- **Tablet** (≤768px): Collapsible sidebar, adjusted padding
- **Mobile** (≤480px): Full-width content, optimized font sizes

## 🔒 Production Deployment

Before deploying:

1. Set `debug=False` in `app.py` line 119
2. Update `host` to appropriate production server
3. Use environment variables for sensitive config
4. Set appropriate CORS origins instead of `"*"`
5. Add database configuration
6. Implement proper authentication

## 📝 Development Notes

- **Frontend Logging**: Open browser DevTools console to see detailed logs
- **Backend Logging**: Check terminal output for server logs
- **Placeholder Routes**: All module endpoints return placeholder responses - implement actual logic during phase development
- **No External Frameworks**: Vanilla JS and CSS only for maximum control and minimal dependencies

## 🎓 Next Phase Features (Coming Soon)

- Database integration (SQLAlchemy ORM)
- User authentication and profiles
- Real data persistence for all modules
- Audio file processing and transcription
- Advanced analytics and reporting
- Mobile app companion

## 📞 Support & Documentation

Each function in `app.py`, HTML, and CSS includes detailed docstrings explaining its purpose and usage.

---

**Created**: 2026 | **Version**: 1.0.0 - Base Setup
