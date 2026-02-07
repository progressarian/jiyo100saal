"""
Route Blueprints
================
"""

from routes.section0 import section0_bp
from routes.section1 import section1_bp
from routes.patients import patients_bp
from routes.assessments import assessments_bp
from routes.pillar1 import bp as pillar1_bp
from routes.pillar2 import bp as pillar2_bp
from routes.reports import bp as reports_bp

__all__ = ['section0_bp', 'section1_bp', 'patients_bp', 'assessments_bp', 'pillar1_bp', 'pillar2_bp', 'reports_bp']
