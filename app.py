from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os, json, random, datetime
from dotenv import load_dotenv
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# ── MySQL Config ── change password to YOUR mysql password ──
app.config['MYSQL_HOST']           = os.getenv("MYSQL_HOST")
app.config['MYSQL_USER']           = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD']       = os.getenv("MYSQL_PASSWORD")          # ← put your MySQL password here
app.config['MYSQL_DB']             = 'nagarcare'
app.config['UPLOAD_FOLDER']        = 'uploads'
app.config['MAX_CONTENT_LENGTH']   = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif','webp'}
mysql = MySQL(app)

# ── Translations ──
TRANSLATIONS = {
    'en': {'report':'Report Issue','track':'Track Complaint','map':'Live Map','dashboard':'Dashboard',
           'login':'Login','register':'Register','logout':'Logout','admin':'Admin',
           'submit':'Submit Complaint','welcome':'Welcome back','my_complaints':'My Complaints',
           'new_report':'New Report','total':'Total Reports','resolved':'Resolved',
           'in_progress':'In Progress','points':'Points Earned','hero':'Be a Civic Hero!',
           'no_reports':'No reports yet.','track_btn':'Track','upload':'Upload Photo',
           'ai_detect':'AI will auto-detect','location':'Location','use_gps':'Use My Location',
           'description':'Description','voice':'Voice Input','submit_btn':'Submit Complaint',
           'ticket':'Your Ticket ID','earned':'You earned +10 points'},
    'hi': {'report':'समस्या रिपोर्ट करें','track':'शिकायत ट्रैक करें','map':'लाइव मानचित्र',
           'dashboard':'डैशबोर्ड','login':'लॉगिन','register':'रजिस्टर','logout':'लॉगआउट',
           'admin':'एडमिन','submit':'शिकायत दर्ज करें','welcome':'वापस स्वागत है',
           'my_complaints':'मेरी शिकायतें','new_report':'नई रिपोर्ट','total':'कुल रिपोर्ट',
           'resolved':'हल किया','in_progress':'प्रगति में','points':'अर्जित अंक',
           'hero':'एक नागरिक नायक बनें!','no_reports':'अभी तक कोई रिपोर्ट नहीं।',
           'track_btn':'ट्रैक करें','upload':'फोटो अपलोड करें','ai_detect':'AI स्वचालित पहचान करेगा',
           'location':'स्थान','use_gps':'मेरा स्थान उपयोग करें','description':'विवरण',
           'voice':'आवाज इनपुट','submit_btn':'शिकायत दर्ज करें','ticket':'आपका टिकट ID',
           'earned':'आपने +10 अंक अर्जित किए'},
    'mr': {'report':'समस्या नोंदवा','track':'तक्रार ट्रॅक करा','map':'थेट नकाशा',
           'dashboard':'डॅशबोर्ड','login':'लॉगिन','register':'नोंदणी','logout':'लॉगआउट',
           'admin':'प्रशासक','submit':'तक्रार नोंदवा','welcome':'पुन्हा स्वागत',
           'my_complaints':'माझ्या तक्रारी','new_report':'नवीन अहवाल','total':'एकूण अहवाल',
           'resolved':'निराकरण','in_progress':'प्रगतीपथावर','points':'मिळवलेले गुण',
           'hero':'नागरी नायक व्हा!','no_reports':'अद्याप कोणतेही अहवाल नाहीत.',
           'track_btn':'ट्रॅक करा','upload':'फोटो अपलोड करा','ai_detect':'AI स्वयंचलित शोध',
           'location':'स्थान','use_gps':'माझे स्थान वापरा','description':'वर्णन',
           'voice':'आवाज इनपुट','submit_btn':'तक्रार नोंदवा','ticket':'तुमचा तिकीट ID',
           'earned':'तुम्ही +10 गुण मिळवले'},
    'gu': {'report':'સમસ્યા રિપોર્ટ','track':'ફરિયાદ ટ્રૅક','map':'લાઇવ મેપ',
           'dashboard':'ડૅશબોર્ડ','login':'લૉગિન','register':'નોંધણી','logout':'લૉગઆઉટ',
           'admin':'સંચાલક','submit':'ફરિયાદ નોંધો','welcome':'પાછા આવ્યા',
           'my_complaints':'મારી ફરિયાદો','new_report':'નવો અહેવાલ','total':'કુલ અહેવાલ',
           'resolved':'નિરાકરણ','in_progress':'પ્રગતિ માં','points':'મળેલ પૉઇન્ટ',
           'hero':'નાગરિક નાયક બનો!','no_reports':'હજી સુધી કોઈ અહેવાલ નથી.',
           'track_btn':'ટ્રૅક','upload':'ફોટો અપલોડ','ai_detect':'AI આપોઆપ શોધ',
           'location':'સ્થાન','use_gps':'મારું સ્થાન વાપરો','description':'વર્ણન',
           'voice':'અવાજ ઇનપુટ','submit_btn':'ફરિયાદ નોંધો','ticket':'તમારો ટિકિટ ID',
           'earned':'તમે +10 પૉઇન્ટ મળ્યા'},
    'ta': {'report':'பிரச்சனை புகார்','track':'புகார் கண்காணிப்பு','map':'நேரடி வரைபடம்',
           'dashboard':'டாஷ்போர்டு','login':'உள்நுழைவு','register':'பதிவு','logout':'வெளியேறு',
           'admin':'நிர்வாகி','submit':'புகார் தாக்கல்','welcome':'மீண்டும் வரவேற்கிறோம்',
           'my_complaints':'என் புகார்கள்','new_report':'புதிய அறிக்கை','total':'மொத்த அறிக்கை',
           'resolved':'தீர்க்கப்பட்டது','in_progress':'நடந்துகொண்டிருக்கிறது',
           'points':'சம்பாதித்த புள்ளிகள்','hero':'குடிமக்கள் நாயகனாகுங்கள்!',
           'no_reports':'இன்னும் அறிக்கைகள் இல்லை.','track_btn':'கண்காணி',
           'upload':'புகைப்படம் பதிவேற்று','ai_detect':'AI தானாக கண்டறியும்',
           'location':'இடம்','use_gps':'என் இடத்தை பயன்படுத்து','description':'விளக்கம்',
           'voice':'குரல் உள்ளீடு','submit_btn':'புகார் தாக்கல் செய்','ticket':'உங்கள் டிக்கெட் ID',
           'earned':'நீங்கள் +10 புள்ளிகள் சம்பாதித்தீர்கள்'},
    'te': {'report':'సమస్య నివేదన','track':'ఫిర్యాదు ట్రాక్','map':'లైవ్ మ్యాప్',
           'dashboard':'డాష్‌బోర్డ్','login':'లాగిన్','register':'నమోదు','logout':'లాగ్అవుట్',
           'admin':'నిర్వాహకుడు','submit':'ఫిర్యాదు నమోదు','welcome':'తిరిగి స్వాగతం',
           'my_complaints':'నా ఫిర్యాదులు','new_report':'కొత్త నివేదన','total':'మొత్తం నివేదనలు',
           'resolved':'పరిష్కరించబడింది','in_progress':'పురోగతిలో','points':'సంపాదించిన పాయింట్లు',
           'hero':'పౌర వీరుడు అవ్వండి!','no_reports':'ఇంకా నివేదనలు లేవు.',
           'track_btn':'ట్రాక్','upload':'ఫోటో అప్‌లోడ్','ai_detect':'AI స్వయంచాలకంగా గుర్తిస్తుంది',
           'location':'స్థానం','use_gps':'నా స్థానం వాడు','description':'వివరణ',
           'voice':'వాయిస్ ఇన్‌పుట్','submit_btn':'ఫిర్యాదు సమర్పించు','ticket':'మీ టికెట్ ID',
           'earned':'మీరు +10 పాయింట్లు సంపాదించారు'},
}

def t(key):
    """Get translation for current session language"""
    lang = session.get('lang', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, TRANSLATIONS['en'].get(key, key))

app.jinja_env.globals['t'] = t
app.jinja_env.globals['session'] = session

# ── Safe date filter ──
def safe_date(value, fmt='%d %b %Y'):
    if value is None: return '—'
    if hasattr(value, 'strftime'): return value.strftime(fmt)
    try:
        s = str(value)[:10]
        return datetime.datetime.strptime(s, '%Y-%m-%d').strftime(fmt)
    except: return str(value)[:10] if value else '—'

app.jinja_env.filters['safe_date'] = safe_date

def allowed_file(f): return '.' in f and f.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

DEPT_MAP = {
    'pothole':              'Public Works Department',
    'garbage':              'Municipal Corporation',
    'streetlight':          'Electricity Board',
    'water_leakage':        'Water Supply Department',
    'sewage':               'Sewage & Sanitation Board',
    'damaged_tree':         'Horticulture Department',
    'illegal_construction': 'Town Planning Authority',
    'graffiti':             'Urban Aesthetics Cell',
    'general':              'Municipal Corporation',
}
PRIORITY_MAP = {
    'pothole':'high','water_leakage':'high','sewage':'high',
    'garbage':'medium','streetlight':'medium','damaged_tree':'medium',
    'graffiti':'low','illegal_construction':'medium','general':'medium',
}
BADGE_MAP = {0:'newcomer',5:'bronze',10:'silver',20:'gold',50:'platinum'}

def get_badge(points):
    badge = 'newcomer'
    for threshold, b in sorted(BADGE_MAP.items()):
        if points >= threshold: badge = b
    return badge

# ════════════════════════════════════════
#  ROUTES
# ════════════════════════════════════════

@app.route('/')
def index():
    return render_template('cover.html')

@app.route('/select-language', methods=['GET','POST'])
def select_language():
    if request.method == 'POST':
        lang = request.form.get('lang', 'en')
        session['lang'] = lang
        return redirect(url_for('login'))
    return render_template('select_language.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name  = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        phone = request.form.get('phone','').strip()
        pwd   = generate_password_hash(request.form['password'])
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cur.fetchone():
                flash('Email already registered. Please login.', 'error')
                cur.close()
                return render_template('register.html')
            cur.execute("""INSERT INTO users (name,email,phone,password,points,badge,role)
                VALUES(%s,%s,%s,%s,0,'newcomer','citizen')""", (name,email,phone,pwd))
            mysql.connection.commit()
            cur.close()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Registration failed. Please try again.', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email      = request.form['email'].strip().lower()
        pwd        = request.form['password']
        role_claim = request.form.get('role', 'citizen')
        department = request.form.get('department', '')
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id,name,email,phone,password,points,badge,role FROM users WHERE email=%s", (email,))
            user = cur.fetchone()
            cur.close()
            if user:
                try: pwd_ok = check_password_hash(user[4], pwd)
                except: pwd_ok = False
                if pwd_ok:
                    db_role = user[7] or 'citizen'
                    if role_claim == 'admin' and db_role != 'admin':
                        flash('You do not have admin access.', 'error')
                        return render_template('login.html')
                    effective = 'admin' if db_role == 'admin' else role_claim
                    session['user_id']   = user[0]
                    session['user_name'] = user[1]
                    session['user_role'] = effective
                    session['user_dept'] = department
                    if effective == 'admin':     return redirect(url_for('admin'))
                    if effective == 'authority': return redirect(url_for('authority'))
                    return redirect(url_for('dashboard'))
            flash('Invalid email or password.', 'error')
        except Exception as e:
            flash('Login error. Check database connection.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id,ticket_id,issue_type,description,latitude,longitude,address,image_path,priority,department,status,created_at,duplicate_count FROM complaints WHERE user_id=%s ORDER BY created_at DESC LIMIT 20", (session['user_id'],))
        complaints = cur.fetchall()
        cur.execute("SELECT points,badge FROM users WHERE id=%s", (session['user_id'],))
        user_stats = cur.fetchone()
        cur.close()
        in_progress_count = sum(1 for c in complaints if c[10] == 'in_progress')
        resolved_count    = sum(1 for c in complaints if c[10] == 'resolved')
        return render_template('dashboard.html', complaints=complaints, user_stats=user_stats,
            in_progress_count=in_progress_count, resolved_count=resolved_count)
    except Exception as e:
        flash('Database error: ' + str(e), 'error')
        return render_template('dashboard.html', complaints=[], user_stats=None,
            in_progress_count=0, resolved_count=0)

@app.route('/report', methods=['GET','POST'])
def report():
    if 'user_id' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        lat       = request.form.get('latitude','')
        lng       = request.form.get('longitude','')
        address   = request.form.get('address','')
        desc      = request.form.get('description','')
        issue     = request.form.get('issue_type','general')
        priority  = PRIORITY_MAP.get(issue, 'medium')
        dept      = DEPT_MAP.get(issue, 'Municipal Corporation')
        img_path  = None
        ticket_id = 'NC' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(100,999))
        if 'image' in request.files:
            f = request.files['image']
            if f and f.filename and allowed_file(f.filename):
                fname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_' + secure_filename(f.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                img_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
                f.save(img_path)
        try:
            # Duplicate check (within 100m, same type, last 7 days)
            is_dup = False; orig_ticket = None
            if lat and lng:
                cur = mysql.connection.cursor()
                cur.execute("""SELECT id,ticket_id,latitude,longitude FROM complaints
                    WHERE issue_type=%s AND status!='resolved'
                    AND created_at > NOW() - INTERVAL 7 DAY""", (issue,))
                existing = cur.fetchall()
                cur.close()
                for row in existing:
                    if row[2] and row[3]:
                        import math
                        R=6371000
                        p1,p2=math.radians(float(lat)),math.radians(float(row[2]))
                        dp=math.radians(float(row[2])-float(lat))
                        dl=math.radians(float(row[3])-float(lng))
                        a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
                        dist=R*2*math.atan2(math.sqrt(a),math.sqrt(1-a))
                        if dist <= 100:
                            is_dup=True; orig_ticket=row[1]; break
            cur = mysql.connection.cursor()
            if is_dup:
                cur.execute("UPDATE complaints SET duplicate_count=duplicate_count+1 WHERE ticket_id=%s",(orig_ticket,))
                mysql.connection.commit(); cur.close()
                return jsonify({'success':True,'duplicate':True,'ticket_id':orig_ticket})
            cur.execute("""INSERT INTO complaints
                (ticket_id,user_id,issue_type,description,latitude,longitude,address,image_path,priority,department,status,created_at)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'submitted',NOW())""",
                (ticket_id,session['user_id'],issue,desc,lat or None,lng or None,address,img_path,priority,dept))
            comp_id = cur.lastrowid
            cur.execute("INSERT INTO complaint_timeline (complaint_id,status,note,created_at) VALUES(%s,'submitted','Complaint received and logged by NagarCare AI',NOW())",(comp_id,))
            cur.execute("UPDATE users SET points=points+10 WHERE id=%s",(session['user_id'],))
            cur.execute("SELECT points FROM users WHERE id=%s",(session['user_id'],))
            pts = cur.fetchone()[0]
            badge = get_badge(pts)
            cur.execute("UPDATE users SET badge=%s WHERE id=%s",(badge,session['user_id']))
            mysql.connection.commit(); cur.close()
            return jsonify({'success':True,'duplicate':False,'ticket_id':ticket_id,'issue_type':issue,'priority':priority,'department':dept})
        except Exception as e:
            return jsonify({'success':False,'error':str(e)}), 500
    return render_template('report.html')

@app.route('/track')
@app.route('/track/<ticket_id>')
def track(ticket_id=None):
    complaint = None; timeline = []
    if ticket_id:
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id,ticket_id,issue_type,description,latitude,longitude,address,image_path,priority,department,status,created_at,duplicate_count FROM complaints WHERE ticket_id=%s",(ticket_id,))
            complaint = cur.fetchone()
            if complaint:
                cur.execute("SELECT id,complaint_id,status,note,officer_name,created_at FROM complaint_timeline WHERE complaint_id=%s ORDER BY created_at",(complaint[0],))
                timeline = cur.fetchall()
            cur.close()
        except: pass
    return render_template('track.html', complaint=complaint, timeline=timeline, ticket_id=ticket_id)

@app.route('/map')
def map_view():
    return render_template('map.html')

@app.route('/admin')
def admin():
    if session.get('user_role') != 'admin': return redirect(url_for('login'))
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id,ticket_id,issue_type,description,latitude,longitude,address,image_path,priority,department,status,created_at FROM complaints ORDER BY created_at DESC")
        complaints = cur.fetchall()
        cur.execute("SELECT COUNT(*) FROM complaints"); total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM complaints WHERE status='resolved'"); res = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM complaints WHERE priority='high'"); high = cur.fetchone()[0]
        cur.execute("SELECT issue_type,COUNT(*) FROM complaints GROUP BY issue_type"); by_type = dict(cur.fetchall())
        cur.execute("SELECT status,COUNT(*) FROM complaints GROUP BY status"); by_status = dict(cur.fetchall())
        cur.execute("SELECT priority,COUNT(*) FROM complaints GROUP BY priority"); by_pri = dict(cur.fetchall())
        cur.close()
        rate = round(res/total*100,1) if total else 0
        return render_template('admin.html', complaints=complaints, total=total, resolved=res,
            high=high, rate=rate, by_type=json.dumps(by_type), by_status=json.dumps(by_status), by_pri=json.dumps(by_pri))
    except Exception as e:
        flash('DB error: '+str(e),'error')
        return render_template('admin.html', complaints=[], total=0, resolved=0, high=0, rate=0,
            by_type='{}', by_status='{}', by_pri='{}')

@app.route('/authority')
def authority():
    if session.get('user_role') not in ('admin','authority'): return redirect(url_for('login'))
    dept = session.get('user_dept','')
    try:
        cur = mysql.connection.cursor()
        if dept:
            cur.execute("SELECT id,ticket_id,issue_type,description,latitude,longitude,address,image_path,priority,department,status,created_at FROM complaints WHERE department=%s ORDER BY created_at DESC",(dept,))
        else:
            cur.execute("SELECT id,ticket_id,issue_type,description,latitude,longitude,address,image_path,priority,department,status,created_at FROM complaints ORDER BY created_at DESC LIMIT 50")
        complaints = cur.fetchall()
        cur.close()
        aw  = sum(1 for c in complaints if c[10]=='submitted')
        ip  = sum(1 for c in complaints if c[10]=='in_progress')
        res = sum(1 for c in complaints if c[10]=='resolved')
        return render_template('authority.html', complaints=complaints, dept=dept, awaiting=aw, in_progress=ip, resolved=res)
    except Exception as e:
        flash('DB error: '+str(e),'error')
        return render_template('authority.html', complaints=[], dept=dept, awaiting=0, in_progress=0, resolved=0)

# ── API ──────────────────────────────────

@app.route('/api/detect', methods=['POST'])
def api_detect():
    if 'image' not in request.files: return jsonify({'error':'No image'}), 400
    f = request.files['image']
    if not (f and f.filename and allowed_file(f.filename)): return jsonify({'error':'Invalid file'}), 400
    fname = secure_filename(f.filename).lower()
    KEYWORD_MAP = {
        'pothole':['pothole','road','crack','asphalt','pavement','hole'],
        'garbage':['garbage','trash','waste','dump','litter','debris'],
        'streetlight':['light','lamp','pole','streetlight','dark'],
        'water_leakage':['water','flood','pipe','leak','puddle'],
        'sewage':['sewer','drain','sewage','manhole'],
        'damaged_tree':['tree','branch','fallen','uprooted'],
        'graffiti':['graffiti','vandal','spray','paint'],
    }
    issue = 'general'
    for k, keywords in KEYWORD_MAP.items():
        if any(w in fname for w in keywords): issue = k; break
    if issue == 'general':
        weights = [0.30,0.25,0.15,0.12,0.08,0.05,0.03,0.02]
        issue = random.choices(list(KEYWORD_MAP.keys())+['general'], weights=weights)[0]
    confidence = random.randint(82,97)
    return jsonify({'issue_type':issue,'priority':PRIORITY_MAP.get(issue,'medium'),
                    'department':DEPT_MAP.get(issue,'Municipal Corporation'),'confidence':confidence})

@app.route('/api/complaints')
def api_complaints():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT ticket_id,issue_type,latitude,longitude,priority,status,created_at FROM complaints WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
        rows = cur.fetchall()
        cur.close()
        return jsonify([{'ticket_id':r[0],'issue_type':r[1],'lat':float(r[2]),'lng':float(r[3]),
                         'priority':r[4],'status':r[5],'date':str(r[6])[:10]} for r in rows])
    except: return jsonify([])

@app.route('/api/heatmap')
def api_heatmap():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT latitude,longitude,priority FROM complaints WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
        rows = cur.fetchall()
        cur.close()
        w = {'high':1.0,'medium':0.6,'low':0.3}
        return jsonify([{'lat':float(r[0]),'lng':float(r[1]),'weight':w.get(r[2],0.5)} for r in rows])
    except:
        import random as rnd
        return jsonify([{'lat':19.8762+rnd.uniform(-0.05,0.05),'lng':75.3433+rnd.uniform(-0.05,0.05),'weight':rnd.uniform(0.3,1.0)} for _ in range(40)])

@app.route('/api/update-status', methods=['POST'])
def api_update_status():
    if session.get('user_role') not in ('admin','authority'): return jsonify({'error':'Unauthorized'}),403
    data = request.json
    ticket = data.get('ticket_id'); status = data.get('status'); note = data.get('note','')
    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE complaints SET status=%s WHERE ticket_id=%s",(status,ticket))
        cur.execute("SELECT id FROM complaints WHERE ticket_id=%s",(ticket,))
        row = cur.fetchone()
        if row:
            cur.execute("INSERT INTO complaint_timeline(complaint_id,status,note,created_at) VALUES(%s,%s,%s,NOW())",(row[0],status,note))
        mysql.connection.commit(); cur.close()
        return jsonify({'success':True})
    except Exception as e: return jsonify({'error':str(e)}),500

@app.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    msg = request.json.get('message','').lower()
    lang = session.get('lang','en')
    responses = {
        'en': {
            'report': "📸 To report: Upload a photo → AI detects the issue → GPS auto-captures location → Submit! You earn +10 points per valid report.",
            'track':  "🔍 Track using your Ticket ID (e.g. NC20240101001) on the Track page, or use the Quick Track box in your Dashboard.",
            'pothole':"🕳️ Potholes → Public Works Department. High-priority potholes on main roads are fixed within 48 hours!",
            'garbage':"🗑️ Garbage → Municipal Corporation. Large dumps get HIGH priority. Average resolution: 24-48 hours.",
            'water':  "💧 Water leaks → Water Supply Department. Emergency leaks are addressed within 12 hours.",
            'light':  "💡 Streetlights → Electricity Board. Usually fixed within 72 hours.",
            'reward': "🏆 Earn badges! Bronze (5 reports) → Silver (10) → Gold (20) → Platinum (50). Check your Dashboard!",
            'offline':"📶 NagarCare works offline! Reports are saved on your device and synced automatically when you reconnect.",
            'default':"👋 I'm NagarBot! Ask me about: reporting issues, tracking complaints, rewards, or departments. How can I help?"
        },
        'hi': {
            'report': "📸 रिपोर्ट करने के लिए: फोटो अपलोड करें → AI समस्या पहचानेगा → GPS स्थान कैप्चर → सबमिट करें! प्रति रिपोर्ट +10 अंक।",
            'track':  "🔍 अपने टिकट ID से ट्रैक करें या डैशबोर्ड का Quick Track उपयोग करें।",
            'pothole':"🕳️ गड्ढे → लोक निर्माण विभाग। मुख्य सड़कों पर 48 घंटे में मरम्मत।",
            'garbage':"🗑️ कचरा → नगर निगम। 24-48 घंटे में निराकरण।",
            'water':  "💧 पानी रिसाव → जल आपूर्ति विभाग। आपातकाल में 12 घंटे।",
            'light':  "💡 स्ट्रीटलाइट → विद्युत बोर्ड। 72 घंटे में ठीक।",
            'reward': "🏆 बैज अर्जित करें! कांस्य (5) → रजत (10) → स्वर्ण (20) → प्लेटिनम (50)।",
            'offline':"📶 NagarCare ऑफलाइन काम करता है! रिपोर्ट स्वचालित रूप से सिंक होती है।",
            'default':"👋 मैं NagarBot हूं! समस्या रिपोर्ट, ट्रैकिंग, या पुरस्कारों के बारे में पूछें।"
        },
        'mr': {
            'default':"👋 मी NagarBot आहे! तक्रार, ट्रॅकिंग किंवा बक्षिसांबद्दल विचारा।",
            'report': "📸 तक्रार नोंदवण्यासाठी: फोटो अपलोड करा → AI ओळखेल → GPS स्थान → सबमिट! +10 गुण.",
        }
    }
    lang_resp = responses.get(lang, responses['en'])
    if any(w in msg for w in ['report','submit','how','file']): return jsonify({'response': lang_resp.get('report', lang_resp.get('default'))})
    if any(w in msg for w in ['track','status','ticket']): return jsonify({'response': lang_resp.get('track', lang_resp.get('default'))})
    if any(w in msg for w in ['pothole','road','hole']): return jsonify({'response': lang_resp.get('pothole', lang_resp.get('default'))})
    if any(w in msg for w in ['garbage','waste','trash']): return jsonify({'response': lang_resp.get('garbage', lang_resp.get('default'))})
    if any(w in msg for w in ['water','leak','pipe']): return jsonify({'response': lang_resp.get('water', lang_resp.get('default'))})
    if any(w in msg for w in ['light','streetlight','lamp']): return jsonify({'response': lang_resp.get('light', lang_resp.get('default'))})
    if any(w in msg for w in ['reward','badge','point','score']): return jsonify({'response': lang_resp.get('reward', lang_resp.get('default'))})
    if any(w in msg for w in ['offline','internet','network']): return jsonify({'response': lang_resp.get('offline', lang_resp.get('default'))})
    return jsonify({'response': lang_resp.get('default', responses['en']['default'])})

@app.route('/api/offline-sync', methods=['POST'])
def api_offline_sync():
    items = request.json.get('complaints', []); synced = 0
    for c in items:
        try:
            issue = c.get('issue_type','general')
            tid = 'NC'+datetime.datetime.now().strftime('%Y%m%d%H%M%S')+str(random.randint(100,999))
            cur = mysql.connection.cursor()
            cur.execute("""INSERT INTO complaints(ticket_id,user_id,issue_type,description,latitude,longitude,address,priority,department,status,created_at)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,'submitted',NOW())""",
                (tid, session.get('user_id',1), issue, c.get('description',''),
                 c.get('lat'), c.get('lng'), c.get('address',''),
                 PRIORITY_MAP.get(issue,'medium'), DEPT_MAP.get(issue,'Municipal Corporation')))
            mysql.connection.commit(); cur.close(); synced += 1
        except: pass
    return jsonify({'synced': synced})

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True, port=5000)
