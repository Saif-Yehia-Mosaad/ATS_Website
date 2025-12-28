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

# --- 2. THEME SETUP (Outlier AI Style) ---
# هذا الجزء هو المسؤول عن الألوان المتدرجة والشكل الزجاجي
st.markdown("""
<style>
    /* 1. Main Background: Gradient similar to Outlier AI (Deep Blue/Purple/Black) */
    .stApp {
        background: rgb(15,23,42);
        background: linear-gradient(160deg, rgba(15,23,42,1) 0%, rgba(30,27,75,1) 50%, rgba(15,23,42,1) 100%);
        font-family: 'Inter', sans-serif;
    }

    /* 2. Containers (Cards) with Glassmorphism */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: rgba(30, 41, 59, 0.4); /* Semi-transparent dark blue */
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(10px); /* The frosted glass effect */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* 3. Inputs (Clean Dark Grey) */
    .stTextInput input, .stTextArea textarea {
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        color: #E2E8F0 !important;
        border-radius: 8px;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #818CF8 !important; /* Indigo glow focus */
        box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.2);
    }

    /* 4. Primary Button (The Gradient Button like the Logo) */
    .stButton button[kind="primary"] {
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%); /* Indigo to Purple */
        color: white;
        border: none;
        padding: 12px 24px;
        font-weight: bold;
        border-radius: 30px; /* Rounded pill shape */
        transition: transform 0.2s;
    }
    .stButton button[kind="primary"]:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }

    /* 5. Secondary Buttons (Add/Edit) */
    .stButton button[kind="secondary"] {
        background-color: transparent;
        border: 1px solid #475569;
        color: #94A3B8;
        border-radius: 8px;
    }
    .stButton button[kind="secondary"]:hover {
        border-color: #E2E8F0;
        color: #E2E8F0;
        background-color: rgba(255,255,255,0.05);
    }

    /* Headers */
    h1, h2, h3 {
        color: #F8FAFC !important;
        font-weight: 700;
    }
    p, label {
        color: #CBD5E1 !important;
    }

    /* Custom Header Bar mimicking the screenshot */
    .custom-header {
        display: flex;
        align-items: center;
        margin-bottom: 30px;
    }
    .logo-circle {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2DD4BF 0%, #8B5CF6 100%); /* Teal to Purple */
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
        color: white;
        margin-right: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Logic & Session State ---
keys = ['experience', 'projects', 'education', 'certs', 'skills', 'languages']
for key in keys:
    if key not in st.session_state: st.session_state[key] = []
if 'edit_target' not in st.session_state: st.session_state.edit_target = None


def clean_text(text):
    if text: return text.encode('latin-1', 'replace').decode('latin-1')
    return ""


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

    def add_item(self, title, subtitle=None, is_bullet=False):
        self.set_font('Times', 'B', 11)
        self.multi_cell(0, 5, clean_text(title))
        if subtitle:
            self.set_font('Times', '', 11)
            if is_bullet:
                lines = subtitle.strip().split('\n')
                for line in lines:
                    if line.strip():
                        cl = line.strip().replace('-', '').replace('•', '').strip()
                        y = self.get_y()
                        self.set_xy(12, y)
                        self.cell(5, 5, chr(149), 0, 0)
                        self.set_xy(17, y)
                        self.multi_cell(0, 5, clean_text(cl))
            else:
                self.multi_cell(0, 5, clean_text(subtitle))
            self.ln(2)


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

    sections = [('Technical Skills', 'skills'), ('Professional Experience', 'experience'),
                ('Technical Projects', 'projects'), ('Education', 'education'),
                ('Certifications', 'certs'), ('Languages', 'languages')]

    for title, key in sections:
        if d[key]:
            pdf.section_title(title)
            for item in d[key]:
                if key in ['experience', 'projects']:
                    pdf.add_item(item['title'], item['desc'], True)
                elif key == 'education':
                    pdf.add_item(item['degree'], item['details'])
                elif key == 'certs':
                    pdf.add_item(item['name'], item['auth'])
                else:
                    pdf.set_font('Times', '', 11)
                    y = pdf.get_y();
                    pdf.set_xy(12, y);
                    pdf.cell(5, 5, chr(149), 0, 0)
                    pdf.set_xy(17, y);
                    pdf.multi_cell(0, 5, clean_text(item['text']))
    return pdf


# --- 4. Render Helper (The Cards) ---
def render_section_card(key, title, label1, label2=None):
    # Using container to create the "Glass Card" effect defined in CSS
    with st.container():
        c1, c2 = st.columns([0.8, 0.2])
        c1.markdown(f"### {title}")

        is_edit = (st.session_state.edit_target and st.session_state.edit_target['section'] == key)
        idx = st.session_state.edit_target['index'] if is_edit else None

        v1, v2 = "", ""
        if is_edit:
            item = st.session_state[key][idx]
            if key in ['experience', 'projects']:
                v1, v2 = item['title'], item['desc']
            elif key == 'education':
                v1, v2 = item['degree'], item['details']
            elif key == 'certs':
                v1, v2 = item['name'], item['auth']
            else:
                v1 = item['text']

        # Inputs
        col_in1, col_in2 = st.columns([1, 2] if label2 else [1, 0.01])
        nv1 = col_in1.text_input(label1, value=v1, key=f"in_{key}_1", placeholder="Type here...")
        nv2 = ""
        if label2:
            nv2 = col_in2.text_area(label2, value=v2, height=100, key=f"in_{key}_2", placeholder="Details...")

        # Buttons
        b_col1, b_col2, _ = st.columns([1, 1, 4])
        if is_edit:
            if b_col1.button("Save", key=f"sv_{key}", type="primary"):
                obj = {}
                if key in ['experience', 'projects']:
                    obj = {'title': nv1, 'desc': nv2}
                elif key == 'education':
                    obj = {'degree': nv1, 'details': nv2}
                elif key == 'certs':
                    obj = {'name': nv1, 'auth': nv2}
                else:
                    obj = {'text': nv1}
                st.session_state[key][idx] = obj
                st.session_state.edit_target = None
                st.rerun()
            if b_col2.button("Cancel", key=f"cn_{key}"):
                st.session_state.edit_target = None
                st.rerun()
        else:
            if b_col1.button("Add", key=f"ad_{key}"):
                if nv1:
                    obj = {}
                    if key in ['experience', 'projects']:
                        obj = {'title': nv1, 'desc': nv2}
                    elif key == 'education':
                        obj = {'degree': nv1, 'details': nv2}
                    elif key == 'certs':
                        obj = {'name': nv1, 'auth': nv2}
                    else:
                        obj = {'text': nv1}
                    st.session_state[key].append(obj)
                    st.rerun()

        # Display Items
        if st.session_state[key]:
            st.markdown("---")
            for i, item in enumerate(st.session_state[key]):
                txt = item['title'] if key in ['experience', 'projects'] else \
                    item['degree'] if key == 'education' else \
                        item['name'] if key == 'certs' else item['text']

                rc1, rc2, rc3 = st.columns([0.85, 0.07, 0.08])
                rc1.caption(f"{i + 1}. {txt}")  # Using caption for cleaner look
                if rc2.button("✎", key=f"e_{key}_{i}"):
                    st.session_state.edit_target = {'section': key, 'index': i}
                    st.rerun()
                if rc3.button("✖", key=f"d_{key}_{i}"):
                    st.session_state[key].pop(i)
                    if is_edit and idx == i: st.session_state.edit_target = None
                    st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)  # Spacer between cards


# --- 5. Main Layout ---

# Header Section with "SY" Gradient Circle (Fake Logo)
st.markdown("""
<div class="custom-header">
    <div class="logo-circle">AI</div>
    <div>
        <h1 style="margin:0; font-size: 2rem;">Resume Builder</h1>
        <p style="margin:0; font-size: 0.9rem; opacity: 0.8;">Create your ATS-friendly profile</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Personal Info (Glass Card)
with st.container():
    st.markdown("### 👤 Identity")
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Full Name", "Saif Eldien Yehia")
    email = c2.text_input("Email")
    phone = c3.text_input("Phone")
    c4, c5, c6 = st.columns(3)
    loc = c4.text_input("Location")
    link = c5.text_input("LinkedIn")
    git = c6.text_input("GitHub")
    summ = st.text_area("Summary", height=80, placeholder="Brief professional summary...")

st.markdown("<br>", unsafe_allow_html=True)

# Content Sections
render_section_card('experience', 'Experience', 'Job Title | Company | Date', 'Description')
render_section_card('projects', 'Projects', 'Project Name', 'Description')
render_section_card('education', 'Education', 'Degree', 'Institution | Date')
render_section_card('skills', 'Skills', 'Skill Name')
render_section_card('certs', 'Certifications', 'Name', 'Authority/Date')
render_section_card('languages', 'Languages', 'Language')

st.divider()

# Generate Button (Gradient Style)
if st.button("✨ GENERATE PDF RESUME", type="primary", use_container_width=True):
    if not name:
        st.error("Name is required!")
    else:
        p_data = {'name': name, 'email': email, 'phone': phone, 'location': loc, 'linkedin': link, 'github': git,
                  'summary': summ}
        l_data = {k: st.session_state[k] for k in keys}
        try:
            pdf = generate_pdf(p_data, l_data)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                with open(tmp.name, "rb") as f:
                    st.success("Resume created successfully!")
                    st.download_button("📥 Download PDF", f, f"{name.replace(' ', '_')}_Resume.pdf", "application/pdf")
            os.unlink(tmp.name)
        except Exception as e:
            st.error(f"Error: {e}")