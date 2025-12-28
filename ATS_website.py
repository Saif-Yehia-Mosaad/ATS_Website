import streamlit as st
from fpdf import FPDF
import tempfile
import os

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Resume AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS STYLING (Outlier AI Theme) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Glassmorphism Cards */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Inputs */
    .stTextInput input, .stTextArea textarea {
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        color: #E2E8F0 !important;
        border-radius: 8px;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #818CF8 !important;
        box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.2);
    }

    /* Buttons */
    .stButton button[kind="primary"] {
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 30px;
        font-weight: bold;
    }
    .stButton button[kind="secondary"] {
        background: transparent;
        border: 1px solid #475569;
        color: #94A3B8;
        border-radius: 8px;
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6 { color: #F8FAFC !important; }
    p, label, span { color: #CBD5E1 !important; }

    /* Header Style */
    .custom-header {
        display: flex;
        align-items: center;
        margin-bottom: 30px;
    }
    .logo-circle {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2DD4BF 0%, #8B5CF6 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        margin-right: 15px;
        font-size: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Session State ---
keys = ['experience', 'projects', 'education', 'certs', 'skills', 'languages']
for key in keys:
    if key not in st.session_state: st.session_state[key] = []
if 'edit_target' not in st.session_state: st.session_state.edit_target = None


def clean_text(text):
    if text: return text.encode('latin-1', 'replace').decode('latin-1')
    return ""


# --- 4. PDF Generation Engine ---
class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', '', 10)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def section_title(self, label):
        self.ln(6)
        self.set_font('Times', 'B', 12)
        self.set_text_color(0)
        self.cell(0, 6, label.upper(), 0, 1, 'L')
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def add_item_with_date(self, title, date, subtitle, desc=None, is_bullet=False):
        self.set_font('Times', 'B', 11)

        # Calculate width
        title_w = 140 if date else 190
        self.cell(title_w, 5, clean_text(title), 0, 0, 'L')

        if date:
            self.set_font('Times', '', 11)
            self.cell(0, 5, clean_text(date), 0, 1, 'R')
        else:
            self.ln(5)

        if subtitle:
            self.set_font('Times', 'I', 11)
            self.cell(0, 5, clean_text(subtitle), 0, 1, 'L')

        if desc:
            self.set_font('Times', '', 11)
            if is_bullet:
                lines = desc.strip().split('\n')
                for line in lines:
                    if line.strip():
                        cl = line.strip().replace('-', '').replace('•', '').strip()
                        y = self.get_y()
                        self.set_xy(12, y)
                        self.cell(5, 5, chr(149), 0, 0)
                        self.set_xy(17, y)
                        self.multi_cell(0, 5, clean_text(cl))
            else:
                self.multi_cell(0, 5, clean_text(desc))

        self.ln(2)

    def add_simple_item(self, text):
        self.set_font('Times', '', 11)
        y = self.get_y()
        self.set_xy(12, y)
        self.cell(5, 5, chr(149), 0, 0)
        self.set_xy(17, y)
        self.multi_cell(0, 5, clean_text(text))


def generate_pdf(p, d):
    pdf = PDF('P', 'mm', 'A4')
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()

    pdf.set_font('Times', 'B', 18)
    pdf.cell(0, 8, clean_text(p['name'].upper()), 0, 1, 'C')
    pdf.set_font('Times', '', 11)
    pdf.cell(0, 6, clean_text(f"{p['location']} | {p['phone']} | {p['email']}"), 0, 1, 'C')
    links = [l for l in [p['linkedin'], p['github']] if l]
    if links: pdf.cell(0, 6, " | ".join([clean_text(l) for l in links]), 0, 1, 'C')
    pdf.ln(6)

    if p['summary']:
        pdf.section_title('Professional Summary')
        pdf.set_font('Times', '', 11)
        pdf.multi_cell(0, 5, clean_text(p['summary']))

    if d['experience']:
        pdf.section_title('Professional Experience')
        for item in d['experience']:
            pdf.add_item_with_date(item['title'], item['date'], item['company'], item['desc'], True)

    if d['projects']:
        pdf.section_title('Technical Projects')
        for item in d['projects']:
            pdf.add_item_with_date(item['title'], item['date'], None, item['desc'], True)

    if d['education']:
        pdf.section_title('Education')
        for item in d['education']:
            pdf.add_item_with_date(item['degree'], item['date'], item['school'], None, False)

    if d['certs']:
        pdf.section_title('Certifications')
        for item in d['certs']:
            pdf.add_item_with_date(item['name'], item['date'], item['authority'], None, False)

    if d['skills']:
        pdf.section_title('Technical Skills')
        for item in d['skills']:
            pdf.add_simple_item(item['text'])

    if d['languages']:
        pdf.section_title('Languages')
        for item in d['languages']:
            pdf.add_simple_item(item['text'])

    return pdf


# --- 5. Dynamic Form Component ---
def render_section_manager(key, section_title):
    with st.container():
        c_head, c_count = st.columns([0.8, 0.2])
        c_head.markdown(f"### {section_title}")

        is_edit = (st.session_state.edit_target and st.session_state.edit_target['section'] == key)
        idx = st.session_state.edit_target['index'] if is_edit else None

        defaults = {'f1': '', 'f2': '', 'f3': '', 'f4': ''}

        if is_edit:
            item = st.session_state[key][idx]
            if key == 'experience':
                defaults = {'f1': item['title'], 'f2': item['company'], 'f3': item['date'], 'f4': item['desc']}
            elif key == 'projects':
                defaults = {'f1': item['title'], 'f3': item['date'], 'f4': item['desc']}
            elif key == 'education':
                defaults = {'f1': item['degree'], 'f2': item['school'], 'f3': item['date']}
            elif key == 'certs':
                defaults = {'f1': item['name'], 'f2': item['authority'], 'f3': item['date']}
            elif key in ['skills', 'languages']:
                defaults = {'f1': item['text']}

        # --- INPUTS ---
        # Keys are important here to clear them later
        k1, k2, k3, k4 = f"t_{key}", f"c_{key}", f"d_{key}", f"desc_{key}"

        if key == 'experience':
            c1, c2, c3 = st.columns([1.5, 1.5, 1])
            in_title = c1.text_input("Job Title", value=defaults['f1'], key=k1)
            in_comp = c2.text_input("Company", value=defaults['f2'], key=k2)
            in_date = c3.text_input("Date (Optional)", value=defaults['f3'], key=k3)
            in_desc = st.text_area("Description (Bullets)", value=defaults['f4'], key=k4, height=100)

        elif key == 'education':
            c1, c2, c3 = st.columns([1.5, 1.5, 1])
            in_deg = c1.text_input("Degree", value=defaults['f1'], key=k1)
            in_school = c2.text_input("Institution", value=defaults['f2'], key=k2)
            in_date = c3.text_input("Date (Optional)", value=defaults['f3'], key=k3)

        elif key == 'projects':
            c1, c2 = st.columns([3, 1])
            in_title = c1.text_input("Project Name", value=defaults['f1'], key=k1)
            in_date = c2.text_input("Date (Optional)", value=defaults['f3'], key=k3)
            in_desc = st.text_area("Description (Bullets)", value=defaults['f4'], key=k4, height=100)

        elif key == 'certs':
            c1, c2, c3 = st.columns([1.5, 1.5, 1])
            in_name = c1.text_input("Certification Name", value=defaults['f1'], key=k1)
            in_auth = c2.text_input("Authority", value=defaults['f2'], key=k2)
            in_date = c3.text_input("Date (Optional)", value=defaults['f3'], key=k3)

        else:
            in_text = st.text_input("Item", value=defaults['f1'], key=k1)

        # --- BUTTONS ---
        b1, b2, _ = st.columns([1, 1, 4])

        # Helper to clear inputs
        def clear_inputs():
            if k1 in st.session_state: st.session_state[k1] = ""
            if k2 in st.session_state: st.session_state[k2] = ""
            if k3 in st.session_state: st.session_state[k3] = ""
            if k4 in st.session_state: st.session_state[k4] = ""

        if is_edit:
            if b1.button("Save Changes", key=f"save_{key}", type="primary"):
                new_item = {}
                if key == 'experience':
                    new_item = {'title': in_title, 'company': in_comp, 'date': in_date, 'desc': in_desc}
                elif key == 'education':
                    new_item = {'degree': in_deg, 'school': in_school, 'date': in_date}
                elif key == 'projects':
                    new_item = {'title': in_title, 'date': in_date, 'desc': in_desc}
                elif key == 'certs':
                    new_item = {'name': in_name, 'authority': in_auth, 'date': in_date}
                else:
                    new_item = {'text': in_text}

                st.session_state[key][idx] = new_item
                st.session_state.edit_target = None
                clear_inputs()  # Clear after save too
                st.rerun()

            if b2.button("Cancel", key=f"cancel_{key}", kind="secondary"):
                st.session_state.edit_target = None
                clear_inputs()
                st.rerun()
        else:
            if b1.button("Add Item", key=f"add_{key}", type="secondary"):
                new_item = {}
                valid = False
                if key == 'experience' and in_title:
                    new_item = {'title': in_title, 'company': in_comp, 'date': in_date, 'desc': in_desc}
                    valid = True
                elif key == 'education' and in_deg:
                    new_item = {'degree': in_deg, 'school': in_school, 'date': in_date}
                    valid = True
                elif key == 'projects' and in_title:
                    new_item = {'title': in_title, 'date': in_date, 'desc': in_desc}
                    valid = True
                elif key == 'certs' and in_name:
                    new_item = {'name': in_name, 'authority': in_auth, 'date': in_date}
                    valid = True
                elif key in ['skills', 'languages'] and in_text:
                    new_item = {'text': in_text}
                    valid = True

                if valid:
                    st.session_state[key].append(new_item)
                    clear_inputs()  # <--- HERE IS THE MAGIC (Auto Clear)
                    st.rerun()

        # --- LIST DISPLAY ---
        if st.session_state[key]:
            st.markdown("---")
            for i, item in enumerate(st.session_state[key]):
                display_txt = ""
                if key == 'experience':
                    display_txt = f"{item['title']} @ {item['company']}"
                elif key == 'education':
                    display_txt = f"{item['degree']} - {item['school']}"
                elif key == 'projects':
                    display_txt = item['title']
                elif key == 'certs':
                    display_txt = item['name']
                else:
                    display_txt = item['text']

                if key not in ['skills', 'languages'] and item.get('date'):
                    display_txt += f" ({item['date']})"

                r1, r2, r3 = st.columns([0.85, 0.07, 0.08])
                r1.caption(f"{i + 1}. {display_txt}")
                if r2.button("✎", key=f"e_{key}_{i}"):
                    st.session_state.edit_target = {'section': key, 'index': i}
                    st.rerun()
                if r3.button("✖", key=f"d_{key}_{i}"):
                    st.session_state[key].pop(i)
                    if is_edit and idx == i: st.session_state.edit_target = None
                    st.rerun()


# --- 6. MAIN UI ---
st.markdown("""
<div class="custom-header">
    <div class="logo-circle">AI</div>
    <div>
        <h1 style="margin:0; font-size: 2rem;">Resume Builder</h1>
        <p style="margin:0; font-size: 0.9rem; opacity: 0.8;">Professional & ATS-Friendly</p>
    </div>
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("### 👤 Identity")
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Full Name", "", placeholder="e.g. Saif Eldien")
    email = c2.text_input("Email", placeholder="user@example.com")
    phone = c3.text_input("Phone", placeholder="+20 123 456 7890")
    c4, c5, c6 = st.columns(3)
    loc = c4.text_input("Location", placeholder="Cairo, Egypt")
    link = c5.text_input("LinkedIn")
    git = c6.text_input("GitHub")
    summ = st.text_area("Summary", height=80, placeholder="Brief professional overview...")

st.markdown("<br>", unsafe_allow_html=True)

render_section_manager('experience', 'Professional Experience')
render_section_manager('projects', 'Technical Projects')
render_section_manager('education', 'Education')
render_section_manager('skills', 'Technical Skills')
render_section_manager('certs', 'Certifications')
render_section_manager('languages', 'Languages')

st.divider()

if st.button("✨ GENERATE PDF RESUME", type="primary", use_container_width=True):
    if not name:
        st.error("Please enter your name first!")
    else:
        p_data = {'name': name, 'email': email, 'phone': phone, 'location': loc, 'linkedin': link, 'github': git,
                  'summary': summ}
        l_data = {k: st.session_state[k] for k in keys}

        try:
            pdf = generate_pdf(p_data, l_data)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                with open(tmp.name, "rb") as f:
                    st.success("Resume generated successfully!")
                    st.download_button("📥 Download PDF", f, f"{name.replace(' ', '_')}_Resume.pdf", "application/pdf")
            os.unlink(tmp.name)
        except Exception as e:
            st.error(f"Error: {e}")
