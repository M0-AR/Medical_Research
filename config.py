from datetime import datetime, timedelta

# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your-email@gmail.com',  # Replace with actual email
    'recipients': [
        'recipient1@health.gov',  # Replace with actual recipients
        'recipient2@health.gov'
    ]
}

# Research Sources
RESEARCH_SOURCES = {
    'pubmed': {
        'base_url': 'https://pubmed.ncbi.nlm.nih.gov',
        'enabled': True
    },
    'who': {
        'base_url': 'https://www.who.int/publications',
        'enabled': True
    },
    'clinicaltrials': {
        'base_url': 'https://clinicaltrials.gov',
        'enabled': True
    },
    'medrxiv': {
        'base_url': 'https://www.medrxiv.org',
        'enabled': True
    }
}

# Search Topics
SEARCH_TOPICS = {
    'innovations': [
        'medical technology innovations',
        'healthcare innovations',
        'medical device innovations',
        'digital health innovations'
    ],
    'research': [
        'clinical research breakthroughs',
        'medical research developments',
        'healthcare research findings'
    ],
    'public_health': [
        'public health developments',
        'healthcare policy updates',
        'population health research'
    ],
    'diseases': [
        'infectious disease research',
        'chronic disease management',
        'disease prevention studies'
    ],
    'treatments': [
        'new medical treatments',
        'therapeutic advances',
        'treatment protocols'
    ]
}

# Analysis Settings
ANALYSIS_SETTINGS = {
    'max_papers_per_source': 5,
    'days_to_look_back': 1,  # Only look at papers from the last day
    'min_relevance_score': 0.7,
    'required_fields': ['title', 'abstract', 'authors', 'publication_date']
}

# Dashboard Settings
DASHBOARD_CONFIG = {
    'port': 8080,
    'host': 'localhost',
    'update_interval': 3600,  # Update every hour
    'max_displayed_papers': 50
}

# Database Settings
DATABASE_CONFIG = {
    'filename': 'medical_research.db',
    'backup_dir': 'backups/',
    'backup_interval_hours': 24
}

# Notification Settings
NOTIFICATION_CONFIG = {
    'send_daily_summary': True,
    'send_immediate_alerts': True,
    'alert_keywords': [
        'breakthrough',
        'urgent',
        'emergency',
        'pandemic',
        'outbreak'
    ],
    'summary_time': '08:00',  # When to send daily summary
    'max_alerts_per_day': 5
}

# Report Generation
REPORT_CONFIG = {
    'template_dir': 'templates/',
    'output_dir': 'reports/',
    'formats': ['pdf', 'html'],
    'sections': [
        'executive_summary',
        'key_findings',
        'detailed_analysis',
        'recommendations'
    ]
}

def get_date_range():
    """Get the date range for the current search"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=ANALYSIS_SETTINGS['days_to_look_back'])
    return start_date, end_date
