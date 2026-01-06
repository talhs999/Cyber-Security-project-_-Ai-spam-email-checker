"""
Web Dashboard Application

Flask-based web interface for the Gmail Spam Detection System.
Provides a beautiful dashboard with statistics, email management, and reports.

Features:
- Real-time statistics dashboard
- Email classification history
- Spam email viewer
- Interactive charts and graphs
- Export functionality
"""

from flask import Flask, render_template, jsonify, request, send_file, g
from datetime import datetime, timedelta
import logging
from src.database import EmailDatabase
from src.reports import ReportGenerator
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

def get_db():
    """Get database connection for current request"""
    if 'db' not in g:
        g.db = EmailDatabase(check_same_thread=False)
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Close database connection after request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

logger = logging.getLogger(__name__)


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/stats/summary')
def get_summary_stats():
    """Get overall summary statistics"""
    try:
        stats = get_db().get_summary_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"Error getting summary stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats/weekly')
def get_weekly_stats():
    """Get weekly statistics"""
    try:
        days = request.args.get('days', 7, type=int)
        stats = get_db().get_statistics(days=days)
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"Error getting weekly stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/emails/recent')
def get_recent_emails():
    """Get recent email classifications"""
    try:
        limit = request.args.get('limit', 50, type=int)
        classification = request.args.get('classification', None)
        
        emails = get_db().get_classification_history(limit=limit)
        
        # Filter by classification if specified
        if classification:
            emails = [e for e in emails if e['classification'] == classification.upper()]
        
        return jsonify({
            'success': True,
            'data': emails
        })
    except Exception as e:
        logger.error(f"Error getting recent emails: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/emails/<email_id>/indicators')
def get_email_indicators(email_id):
    """Get threat indicators for a specific email"""
    try:
        indicators = get_db().get_threat_indicators(email_id)
        return jsonify({
            'success': True,
            'data': indicators
        })
    except Exception as e:
        logger.error(f"Error getting indicators: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/reports/export')
def export_report():
    """Export comprehensive report"""
    try:
        filename = f"spam_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_gen = ReportGenerator(get_db())
        report_gen.export_to_file(filename)
        return send_file(filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error exporting report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/charts/classification')
def get_classification_chart_data():
    """Get data for classification pie chart"""
    try:
        stats = get_db().get_summary_stats()
        return jsonify({
            'success': True,
            'data': {
                'labels': ['Safe', 'Suspicious', 'Spam'],
                'values': [
                    stats.get('safe', 0),
                    stats.get('suspicious', 0),
                    stats.get('spam', 0)
                ],
                'colors': ['#10b981', '#f59e0b', '#ef4444']
            }
        })
    except Exception as e:
        logger.error(f"Error getting chart data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/database/reset', methods=['POST'])
def reset_database():
    """Reset all database data"""
    try:
        success = get_db().clear_all_data()
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to clear database'}), 500
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/charts/weekly-trend')
def get_weekly_trend_data():
    """Get data for weekly trend chart"""
    try:
        stats = get_db().get_statistics(days=7)
        
        # Reverse to show oldest to newest
        stats.reverse()
        
        return jsonify({
            'success': True,
            'data': {
                'labels': [s['date'] for s in stats],
                'datasets': [
                    {
                        'label': 'Safe',
                        'data': [s['safe_count'] for s in stats],
                        'borderColor': '#10b981',
                        'backgroundColor': 'rgba(16, 185, 129, 0.1)'
                    },
                    {
                        'label': 'Suspicious',
                        'data': [s['suspicious_count'] for s in stats],
                        'borderColor': '#f59e0b',
                        'backgroundColor': 'rgba(245, 158, 11, 0.1)'
                    },
                    {
                        'label': 'Spam',
                        'data': [s['spam_count'] for s in stats],
                        'borderColor': '#ef4444',
                        'backgroundColor': 'rgba(239, 68, 68, 0.1)'
                    }
                ]
            }
        })
    except Exception as e:
        logger.error(f"Error getting trend data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def run_dashboard(host='127.0.0.1', port=5000, debug=True):
    """Run the web dashboard"""
    print("\n" + "="*60)
    print("Gmail Spam Detection - Web Dashboard")
    print("="*60)
    print(f"\nDashboard URL: http://{host}:{port}")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_dashboard()
