# from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
# from werkzeug.security import generate_password_hash, check_password_hash
# import sqlite3
# import json
# from datetime import datetime, timedelta
# import os
# from functools import wraps
# import ee
# import io
# from reportlab.lib.pagesizes import letter, A4
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
# from reportlab.lib.units import inch
# import base64
# from io import BytesIO

# app = Flask(__name__)
# app.secret_key = 'your-secret-key-here-change-in-production'

# # Initialize Google Earth Engine
# try:
#     import ee
#     EE_AVAILABLE = True
#     try:
#         ee.Initialize(project="location-473308")
#     except Exception:
#         EE_AVAILABLE = False
# except Exception:
#     EE_AVAILABLE = False

    

# # Database setup
# def init_db():
#     conn = sqlite3.connect('crop_monitoring.db')
#     c = conn.cursor()
    
#     # Users table
#     c.execute('''CREATE TABLE IF NOT EXISTS users
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                   username TEXT UNIQUE NOT NULL,
#                   email TEXT UNIQUE NOT NULL,
#                   password TEXT NOT NULL,
#                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
#     # Fields table
#     c.execute('''CREATE TABLE IF NOT EXISTS fields
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                   user_id INTEGER NOT NULL,
#                   field_name TEXT NOT NULL,
#                   crop_type TEXT NOT NULL,
#                   planting_date DATE NOT NULL,
#                   acres REAL NOT NULL,
#                   geometry TEXT NOT NULL,
#                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                   FOREIGN KEY (user_id) REFERENCES users (id))''')
    
#     # NDVI data table
#     c.execute('''CREATE TABLE IF NOT EXISTS ndvi_data
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                   field_id INTEGER NOT NULL,
#                   date DATE NOT NULL,
#                   ndvi_mean REAL,
#                   ndvi_min REAL,
#                   ndvi_max REAL,
#                   ndvi_std REAL,
#                   evi_mean REAL,
#                   savi_mean REAL,
#                   moisture_index REAL,
#                   FOREIGN KEY (field_id) REFERENCES fields (id),
#                   UNIQUE(field_id, date))''')
    
#     # Alerts table
#     c.execute('''CREATE TABLE IF NOT EXISTS alerts
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                   field_id INTEGER NOT NULL,
#                   alert_type TEXT NOT NULL,
#                   priority TEXT NOT NULL,
#                   message TEXT NOT NULL,
#                   suggestion TEXT,
#                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                   resolved BOOLEAN DEFAULT 0,
#                   FOREIGN KEY (field_id) REFERENCES fields (id))''')
    
#     conn.commit()
#     conn.close()

# init_db()

# # Login required decorator
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#     return decorated_function

# # Helper function to get DB connection
# def get_db():
#     conn = sqlite3.connect('crop_monitoring.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# # Routes
# @app.route('/')
# def index():
#     if 'user_id' in session:
#         return redirect(url_for('dashboard'))
#     return redirect(url_for('login'))

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         data = request.json
#         username = data.get('username')
#         email = data.get('email')
#         password = data.get('password')
        
#         conn = get_db()
#         c = conn.cursor()
        
#         try:
#             hashed_password = generate_password_hash(password)
#             c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
#                      (username, email, hashed_password))
#             conn.commit()
#             conn.close()
#             return jsonify({'success': True, 'message': 'Registration successful'})
#         except sqlite3.IntegrityError:
#             conn.close()
#             return jsonify({'success': False, 'message': 'Username or email already exists'})
    
#     return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         data = request.json
#         username = data.get('username')
#         password = data.get('password')
        
#         conn = get_db()
#         c = conn.cursor()
#         c.execute('SELECT * FROM users WHERE username = ?', (username,))
#         user = c.fetchone()
#         conn.close()
        
#         if user and check_password_hash(user['password'], password):
#             session['user_id'] = user['id']
#             session['username'] = user['username']
#             return jsonify({'success': True})
#         else:
#             return jsonify({'success': False, 'message': 'Invalid credentials'})
    
#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('login'))

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     return render_template('dashboard.html')

# @app.route('/add-field')
# @login_required
# def add_field():
#     return render_template('add_field.html')

# @app.route('/analytics')
# @login_required
# def analytics():
#     return render_template('analytics.html')

# @app.route('/alerts')
# @login_required
# def alerts():
#     return render_template('alerts.html')

# @app.route('/report')
# @login_required
# def report():
#     return render_template('report.html')

# # API Routes
# @app.route('/api/dashboard-stats')
# @login_required
# def dashboard_stats():
#     conn = get_db()
#     c = conn.cursor()
    
#     # Get total fields and acres
#     c.execute('''SELECT COUNT(*) as total_fields, SUM(acres) as total_acres 
#                  FROM fields WHERE user_id = ?''', (session['user_id'],))
#     stats = c.fetchone()
    
#     # Get unresolved alerts count
#     c.execute('''SELECT COUNT(*) as total_alerts FROM alerts 
#                  WHERE field_id IN (SELECT id FROM fields WHERE user_id = ?) 
#                  AND resolved = 0''', (session['user_id'],))
#     alerts_count = c.fetchone()
    
#     # Get all fields overview
#     c.execute('''SELECT f.*, 
#                  (SELECT COUNT(*) FROM alerts WHERE field_id = f.id AND resolved = 0) as alert_count
#                  FROM fields f WHERE f.user_id = ?
#                  ORDER BY f.created_at DESC''', (session['user_id'],))
#     fields = [dict(row) for row in c.fetchall()]
    
#     conn.close()
    
#     return jsonify({
#         'total_fields': stats['total_fields'] or 0,
#         'total_acres': round(stats['total_acres'] or 0, 2),
#         'total_alerts': alerts_count['total_alerts'] or 0,
#         'fields': fields
#     })

# @app.route('/api/add-field', methods=['POST'])
# @login_required
# def api_add_field():
#     data = request.json
    
#     conn = get_db()
#     c = conn.cursor()
    
#     try:
#         c.execute('''INSERT INTO fields (user_id, field_name, crop_type, planting_date, acres, geometry)
#                      VALUES (?, ?, ?, ?, ?, ?)''',
#                  (session['user_id'], data['field_name'], data['crop_type'], 
#                   data['planting_date'], data['acres'], json.dumps(data['geometry'])))
#         field_id = c.lastrowid
#         conn.commit()
#         conn.close()
        
#         # Initialize NDVI data collection for this field
#         collect_ndvi_data(field_id)
        
#         return jsonify({'success': True, 'field_id': field_id})
#     except Exception as e:
#         conn.close()
#         return jsonify({'success': False, 'message': str(e)})

# @app.route('/api/fields')
# @login_required
# def get_fields():
#     conn = get_db()
#     c = conn.cursor()
#     c.execute('SELECT * FROM fields WHERE user_id = ? ORDER BY created_at DESC', 
#               (session['user_id'],))
#     fields = [dict(row) for row in c.fetchall()]
#     conn.close()
    
#     for field in fields:
#         field['geometry'] = json.loads(field['geometry'])
    
#     return jsonify(fields)

# @app.route('/api/field/<int:field_id>/ndvi-data')
# @login_required
# def get_ndvi_data(field_id):
#     start_date = request.args.get('start_date')
#     end_date = request.args.get('end_date')
    
#     conn = get_db()
#     c = conn.cursor()
    
#     # Verify field belongs to user
#     c.execute('SELECT * FROM fields WHERE id = ? AND user_id = ?', 
#               (field_id, session['user_id']))
#     field = c.fetchone()
    
#     if not field:
#         conn.close()
#         return jsonify({'error': 'Field not found'}), 404
    
#     # Get NDVI data
#     query = 'SELECT * FROM ndvi_data WHERE field_id = ?'
#     params = [field_id]
    
#     if start_date and end_date:
#         query += ' AND date BETWEEN ? AND ?'
#         params.extend([start_date, end_date])
    
#     query += ' ORDER BY date ASC'
    
#     c.execute(query, params)
#     data = [dict(row) for row in c.fetchall()]
#     conn.close()
    
#     return jsonify(data)

# @app.route('/api/field/<int:field_id>/update-ndvi', methods=['POST'])
# @login_required
# def update_field_ndvi(field_id):
#     conn = get_db()
#     c = conn.cursor()
    
#     # Verify field belongs to user
#     c.execute('SELECT * FROM fields WHERE id = ? AND user_id = ?', 
#               (field_id, session['user_id']))
#     field = c.fetchone()
#     conn.close()
    
#     if not field:
#         return jsonify({'error': 'Field not found'}), 404
    
#     # Collect latest NDVI data
#     collect_ndvi_data(field_id)
    
#     # Check for alerts
#     check_field_alerts(field_id)
    
#     return jsonify({'success': True})

# @app.route('/api/alerts')
# @login_required
# def get_alerts():
#     conn = get_db()
#     c = conn.cursor()
    
#     c.execute('''SELECT a.*, f.field_name, f.crop_type 
#                  FROM alerts a
#                  JOIN fields f ON a.field_id = f.id
#                  WHERE f.user_id = ? AND a.resolved = 0
#                  ORDER BY 
#                    CASE a.priority 
#                      WHEN 'Critical' THEN 1
#                      WHEN 'High' THEN 2
#                      WHEN 'Medium' THEN 3
#                      WHEN 'Low' THEN 4
#                    END,
#                    a.created_at DESC''', (session['user_id'],))
    
#     alerts = [dict(row) for row in c.fetchall()]
#     conn.close()
    
#     return jsonify(alerts)

# @app.route('/api/alert/<int:alert_id>/resolve', methods=['POST'])
# @login_required
# def resolve_alert(alert_id):
#     conn = get_db()
#     c = conn.cursor()
    
#     c.execute('''UPDATE alerts SET resolved = 1 
#                  WHERE id = ? AND field_id IN 
#                  (SELECT id FROM fields WHERE user_id = ?)''', 
#               (alert_id, session['user_id']))
    
#     conn.commit()
#     conn.close()
    
#     return jsonify({'success': True})

# @app.route('/api/generate-report', methods=['POST'])
# @login_required
# def generate_report():
#     data = request.json
#     field_id = data.get('field_id')
#     start_date = data.get('start_date')
#     end_date = data.get('end_date')
    
#     # Generate PDF report
#     pdf_buffer = create_pdf_report(field_id, start_date, end_date)
    
#     return send_file(
#         pdf_buffer,
#         mimetype='application/pdf',
#         as_attachment=True,
#         download_name=f'field_report_{field_id}_{datetime.now().strftime("%Y%m%d")}.pdf'
#     )

# # Helper functions
# def collect_ndvi_data(field_id):
#     """Collect NDVI and vegetation indices from Google Earth Engine"""
#     try:
#         conn = get_db()
#         c = conn.cursor()
        
#         c.execute('SELECT * FROM fields WHERE id = ?', (field_id,))
#         field = c.fetchone()
        
#         if not field:
#             conn.close()
#             return
        
#         # Parse geometry
#         geometry = json.loads(field['geometry'])
#         coords = geometry['coordinates'][0]
        
#         # Create Earth Engine geometry
#         ee_geometry = ee.Geometry.Polygon(coords)
        
#         # Get the last recorded date
#         c.execute('SELECT MAX(date) as last_date FROM ndvi_data WHERE field_id = ?', (field_id,))
#         last_record = c.fetchone()
        
#         if last_record['last_date']:
#             start_date = datetime.strptime(last_record['last_date'], '%Y-%m-%d') + timedelta(days=1)
#         else:
#             start_date = datetime.strptime(field['planting_date'], '%Y-%m-%d')
        
#         end_date = datetime.now()
        
#         # Collect data day by day
#         current_date = start_date
#         while current_date <= end_date:
#             date_str = current_date.strftime('%Y-%m-%d')
#             next_date_str = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
            
#             try:
#                 # Get Sentinel-2 imagery
#                 collection = ee.ImageCollection('COPERNICUS/S2_SR') \
#                     .filterBounds(ee_geometry) \
#                     .filterDate(date_str, next_date_str) \
#                     .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                
#                 if collection.size().getInfo() > 0:
#                     image = collection.median()
                    
#                     # Calculate indices
#                     ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
#                     evi = image.expression(
#                         '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
#                         {
#                             'NIR': image.select('B8'),
#                             'RED': image.select('B4'),
#                             'BLUE': image.select('B2')
#                         }
#                     ).rename('EVI')
                    
#                     savi = image.expression(
#                         '((NIR - RED) / (NIR + RED + 0.5)) * 1.5',
#                         {
#                             'NIR': image.select('B8'),
#                             'RED': image.select('B4')
#                         }
#                     ).rename('SAVI')
                    
#                     moisture = image.normalizedDifference(['B8', 'B11']).rename('MOISTURE')
                    
#                     # Get statistics
#                     stats = ee.Image.cat([ndvi, evi, savi, moisture]).reduceRegion(
#                         reducer=ee.Reducer.mean().combine(
#                             ee.Reducer.minMax(), '', True
#                         ).combine(
#                             ee.Reducer.stdDev(), '', True
#                         ),
#                         geometry=ee_geometry,
#                         scale=10,
#                         maxPixels=1e9
#                     ).getInfo()
                    
#                     # Insert into database
#                     c.execute('''INSERT OR REPLACE INTO ndvi_data 
#                                  (field_id, date, ndvi_mean, ndvi_min, ndvi_max, ndvi_std, 
#                                   evi_mean, savi_mean, moisture_index)
#                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
#                              (field_id, date_str,
#                               stats.get('NDVI_mean'),
#                               stats.get('NDVI_min'),
#                               stats.get('NDVI_max'),
#                               stats.get('NDVI_stdDev'),
#                               stats.get('EVI_mean'),
#                               stats.get('SAVI_mean'),
#                               stats.get('MOISTURE_mean')))
#             except Exception as e:
#                 print(f"Error processing {date_str}: {str(e)}")
            
#             current_date += timedelta(days=1)
        
#         conn.commit()
#         conn.close()
#     except Exception as e:
#         print(f"Error in collect_ndvi_data: {str(e)}")

# def check_field_alerts(field_id):
#     """Check field data and generate alerts"""
#     conn = get_db()
#     c = conn.cursor()
    
#     # Get recent NDVI data
#     c.execute('''SELECT * FROM ndvi_data 
#                  WHERE field_id = ? 
#                  ORDER BY date DESC LIMIT 7''', (field_id,))
#     recent_data = [dict(row) for row in c.fetchall()]
    
#     if not recent_data:
#         conn.close()
#         return
    
#     latest = recent_data[0]
    
#     # Check for low NDVI (poor vegetation health)
#     if latest['ndvi_mean'] and latest['ndvi_mean'] < 0.3:
#         c.execute('''INSERT INTO alerts (field_id, alert_type, priority, message, suggestion)
#                      VALUES (?, ?, ?, ?, ?)''',
#                  (field_id, 'Low Vegetation Health', 'High',
#                   f'NDVI value is {latest["ndvi_mean"]:.2f}, indicating poor vegetation health',
#                   'Consider soil testing, check for pest infestation, ensure adequate irrigation and nutrition'))
    
#     # Check for declining trend
#     if len(recent_data) >= 7:
#         avg_recent = sum(d['ndvi_mean'] or 0 for d in recent_data[:3]) / 3
#         avg_older = sum(d['ndvi_mean'] or 0 for d in recent_data[4:7]) / 3
        
#         if avg_recent < avg_older * 0.9:
#             c.execute('''INSERT INTO alerts (field_id, alert_type, priority, message, suggestion)
#                          VALUES (?, ?, ?, ?, ?)''',
#                      (field_id, 'Declining Vegetation', 'Medium',
#                       'Vegetation health is declining over the past week',
#                       'Investigate possible causes: water stress, nutrient deficiency, or disease'))
    
#     # Check moisture levels
#     if latest['moisture_index'] and latest['moisture_index'] < 0.2:
#         c.execute('''INSERT INTO alerts (field_id, alert_type, priority, message, suggestion)
#                      VALUES (?, ?, ?, ?, ?)''',
#                  (field_id, 'Low Soil Moisture', 'Critical',
#                   f'Moisture index is {latest["moisture_index"]:.2f}, indicating water stress',
#                   'Immediate irrigation recommended. Check irrigation system functionality'))
    
#     conn.commit()
#     conn.close()

# def create_pdf_report(field_id, start_date, end_date):
#     """Create PDF report for a field"""
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter)
#     elements = []
#     styles = getSampleStyleSheet()
    
#     # Get field data
#     conn = get_db()
#     c = conn.cursor()
    
#     c.execute('SELECT * FROM fields WHERE id = ?', (field_id,))
#     field = dict(c.fetchone())
    
#     c.execute('''SELECT * FROM ndvi_data 
#                  WHERE field_id = ? AND date BETWEEN ? AND ?
#                  ORDER BY date ASC''', (field_id, start_date, end_date))
#     ndvi_data = [dict(row) for row in c.fetchall()]
    
#     conn.close()
    
#     # Title
#     title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#2c3e50'))
#     elements.append(Paragraph(f"Field Report: {field['field_name']}", title_style))
#     elements.append(Spacer(1, 0.3*inch))
    
#     # Field Information
#     field_info = [
#         ['Field Name:', field['field_name']],
#         ['Crop Type:', field['crop_type']],
#         ['Planting Date:', field['planting_date']],
#         ['Area:', f"{field['acres']} acres"],
#         ['Report Period:', f"{start_date} to {end_date}"]
#     ]
    
#     field_table = Table(field_info, colWidths=[2*inch, 4*inch])
#     field_table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#         ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
#         ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
#     ]))
    
#     elements.append(field_table)
#     elements.append(Spacer(1, 0.3*inch))
    
#     # NDVI Statistics
#     if ndvi_data:
#         avg_ndvi = sum(d['ndvi_mean'] or 0 for d in ndvi_data) / len(ndvi_data)
#         max_ndvi = max(d['ndvi_mean'] or 0 for d in ndvi_data)
#         min_ndvi = min(d['ndvi_mean'] or 0 for d in ndvi_data)
        
#         elements.append(Paragraph("Vegetation Health Summary", styles['Heading2']))
#         elements.append(Spacer(1, 0.2*inch))
        
#         stats_data = [
#             ['Metric', 'Value', 'Status'],
#             ['Average NDVI', f'{avg_ndvi:.3f}', get_ndvi_status(avg_ndvi)],
#             ['Maximum NDVI', f'{max_ndvi:.3f}', ''],
#             ['Minimum NDVI', f'{min_ndvi:.3f}', ''],
#             ['Data Points', str(len(ndvi_data)), '']
#         ]
        
#         stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
#         stats_table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('FONTSIZE', (0, 0), (-1, -1), 10),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#             ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')])
#         ]))
        
#         elements.append(stats_table)
#         elements.append(Spacer(1, 0.3*inch))
        
#         # Recommendations
#         elements.append(Paragraph("Recommendations", styles['Heading2']))
#         elements.append(Spacer(1, 0.2*inch))
        
#         recommendations = get_field_recommendations(field['crop_type'], avg_ndvi, ndvi_data)
#         for rec in recommendations:
#             elements.append(Paragraph(f"• {rec}", styles['Normal']))
#             elements.append(Spacer(1, 0.1*inch))
    
#     doc.build(elements)
#     buffer.seek(0)
#     return buffer

# def get_ndvi_status(ndvi):
#     """Get NDVI health status"""
#     if ndvi >= 0.6:
#         return 'Excellent'
#     elif ndvi >= 0.4:
#         return 'Good'
#     elif ndvi >= 0.3:
#         return 'Fair'
#     else:
#         return 'Poor'

# def get_field_recommendations(crop_type, avg_ndvi, ndvi_data):
#     """Generate recommendations based on field data"""
#     recommendations = []
    
#     if avg_ndvi < 0.3:
#         recommendations.append("Vegetation health is poor. Conduct soil testing and check irrigation systems.")
#         recommendations.append("Consider applying appropriate fertilizers based on soil test results.")
#     elif avg_ndvi < 0.5:
#         recommendations.append("Vegetation health is moderate. Monitor closely for any declining trends.")
#         recommendations.append("Ensure consistent watering schedule is maintained.")
#     else:
#         recommendations.append("Vegetation health is good. Continue current management practices.")
    
#     # Check for trends
#     if len(ndvi_data) >= 7:
#         recent_avg = sum(d['ndvi_mean'] or 0 for d in ndvi_data[:3]) / 3
#         older_avg = sum(d['ndvi_mean'] or 0 for d in ndvi_data[-3:]) / 3
        
#         if recent_avg > older_avg * 1.1:
#             recommendations.append("Positive growth trend observed. Your crop is responding well to current conditions.")
#         elif recent_avg < older_avg * 0.9:
#             recommendations.append("Declining trend detected. Investigate possible stressors immediately.")
    
#     recommendations.append(f"For {crop_type}, ensure you're following crop-specific best practices for this growth stage.")
    
#     return recommendations

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)

