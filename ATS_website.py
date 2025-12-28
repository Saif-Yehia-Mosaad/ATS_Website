"""
=============================================================================
PROJECT: ULTIMATE ATS RESUME BUILDER (PRO EDITION)
AUTHOR: AI ASSISTANT
VERSION: 5.1.0 (Clean & Professional)
DESCRIPTION:
    A robust, privacy-focused, ATS-optimized resume builder.
    - No personal data hardcoded.
    - Professional placeholders (e.g., John Doe).
    - Enterprise-grade architecture.
=============================================================================
"""

import streamlit as st
from fpdf import FPDF
import tempfile
import os
import re
from datetime import datetime

# =============================================================================
# 1. APP CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Professional Resume Builder",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Constants
MAX_SUMMARY_CHARS = 2000
SECTIONS = ['experience', 'projects', 'education', 'certs', 'skills', 'languages']

# =============================================================================
# 2. CSS STYLING (THEME)
# =============================================================================

st.markdown("""
<style>
    /* Global Font & Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(170deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #F8FAFC;
    }

    /* Cards */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }

    /* Inputs */
    .stTextInput input, .stTextArea textarea {
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        color: #F8FAFC !important;
        border-radius: 8px;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.3);
    }

    /* Buttons */
    .stButton button[kind="primary"] {
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 13px;
    }
    .stButton button[kind="secondary"] {
        background: transparent;
        border: 1px solid #475569;
        color: #94A3B8;
        border-radius: 8px;
    }
    
    /* Typography */
    h1, h2, h3, h4 { color: #F8FAFC !important; }
    p, label, span, div { color: #E2E8F0 !important; }
    .stToast { background-color: #1E293B !important; color: white !important; border: 1px solid #475569; }
    
    /* Header Gradient */
    .gradient-text {
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 3. UTILITIES
# =============================================================================

def clean_text(text: str) -> str:
    """Sanitizes text for PDF generation."""
    if not text: return ""
    replacements = {'–': '-', '—': '-', '“': '"', '”': '"', '’': "'", '‘': "'", '•': '-'}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode('latin-1', 'replace').decode('latin-1')

def validate_email(email: str) -> bool:
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email) is not None

# =============================================================================
# 4. STATE MANAGEMENT
# =============================================================================

for key in SECTIONS:
    if key not in st.session_state: st.session_state[key] = []
if 'edit_target' not in st.session_state: st.session_state.edit_target = None

# =============================================================================
# 5. CALLBACKS (LOGIC LAYER)
# =============================================================================

def add_item_callback(section_key):
    k1, k2, k3, k4 = f"t_{section_key}", f"c_{section_key}", f"d_{section_key}", f"desc_{section_key}"
    v1 = st.session_state.get(k1, "").strip()
    v2 = st.session_state.get(k2, "").strip()
    v3 = st.session_state.get(k3, "").strip()
    v4 = st.session_state.get(k4, "").strip()

    valid = False
    new_item = {}

    if section_key == 'experience' and v1:
        new_item = {'title': v1, 'company': v2, 'date': v3, 'desc': v4}; valid = True
    elif section_key == 'education' and v1:
        new_item = {'degree': v1, 'school': v2, 'date': v3}; valid = True
    elif section_key == 'projects' and v1:
        new_item = {'title': v1, 'date': v3, 'desc': v4}; valid = True
    elif section_key == 'certs' and v1:
        new_item = {'name': v1, 'authority': v2, 'date': v3}; valid = True
    elif section_key in ['skills', 'languages'] and v1:
        new_item = {'text': v1}; valid = True

    if valid:
        st.session_state[section_key].append(new_item)
        for k in [k1, k2, k3, k4]:
            if k in st.session_state: st.session_state[k] = ""
        st.toast(f"✅ Added to {section_key.capitalize()}")
    else:
        st.toast("⚠️ Main field is required!", icon="🚨")

def save_changes_callback(section_key, idx):
    k1, k2, k3, k4 = f"t_{section_key}", f"c_{section_key}", f"d_{section_key}", f"desc_{section_key}"
    v1 = st.session_state.get(k1, "").strip()
    v2 = st.session_state.get(k2, "").strip()
    v3 = st.session_state.get(k3, "").strip()
    v4 = st.session_state.get(k4, "").strip()

    new_item = {}
    if section_key == 'experience': new_item = {'title': v1, 'company': v2, 'date': v3, 'desc': v4}
    elif section_key == 'education': new_item = {'degree': v1, 'school': v2, 'date': v3}
    elif section_key == 'projects': new_item = {'title': v1, 'date': v3, 'desc': v4}
    elif section_key == 'certs': new_item = {'name': v1, 'authority': v2, 'date': v3}
    else: new_item = {'text': v1}

    st.session_state[section_key][idx] = new_item
    st.session_state.edit_target = None
    for k in [k1, k2, k3, k4]:
        if k in st.session_state: st.session_state[k] = ""
    st.toast("💾 Saved Successfully")

def cancel_edit_callback(section_key):
    st.session_state.edit_target = None
    for k in [f"t_{section_key}", f"c_{section_key}", f"d_{section_key}", f"desc_{section_key}"]:
        if k in st.session_state: st.session_state[k] = ""

def delete_item_callback(section_key, idx):
    st.session_state[section_key].pop(idx)
    if st.session_state.edit_target and st.session_state.edit_target['section'] == section_key and st.session_state.edit_target['index'] == idx:
        st.session_state.edit_target = None
    st.toast("🗑️ Item Deleted")

def trigger_edit_callback(section_key, idx):
    st.session_state.edit_target = {'section': section_key, 'index': idx}
    item = st.session_state[section_key][idx]
    if section_key == 'experience':
        st.session_state[f"t_{section_key}"] = item['title']
        st.session_state[f"c_{section_key}"] = item['company']
        st.session_state[f"d_{section_key}"] = item['date']
        st.session_state[f"desc_{section_key}"] = item['desc']
    elif section_key == 'education':
        st.session_state[f"t_{section_key}"] = item['degree']
        st.session_state[f"c_{section_key}"] = item['school']
        st.session_state[f"d_{section_key}"] = item['date']
    elif section_key == 'projects':
        st.session_state[f"t_{section_key}"] = item['title']
        st.session_state[f"d_{section_key}"] = item['date']
        st.session_state[f"desc_{section_key}"] = item['desc']
    elif section_key == 'certs':
        st.session_state[f"t_{section_key}"] = item['name']
        st.session_state[f"c_{section_key}"] = item['authority']
        st.session_state[f"d_{section_key}"] = item['date']
    else:
        st.session_state[f"t_{section_key}"] = item['text']

# =============================================================================
# 6. PDF ENGINE
# =============================================================================

class UltimateATSPDF(FPDF):
    def header(self): pass
    def footer(self):
        self.set_y(-15)
        self.set_font('Times', '', 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def draw_section_title(self, title):
        self.ln(6)
        self.set_font('Times', 'B', 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, title.upper(), 0, 1, 'L')
        self.set_draw_color(0, 0, 0)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def draw_complex_item(self, title, subtitle, date, description, is_list=True):
        self.set_font('Times', 'B', 10)
        self.set_text_color(0, 0, 0)
        title_w = 140 if date else 190
        self.cell(title_w, 5, clean_text(title), 0, 0, 'L')

        if date:
            self.set_font('Times', '', 10)
            self.cell(0, 5, clean_text(date), 0, 1, 'R')
        else:
            self.ln(5)

        if subtitle:
            self.set_font('Times', 'I', 10)
            self.cell(0, 5, clean_text(subtitle), 0, 1, 'L')

        if description:
            self.set_font('Times', '', 10)
            lines = description.strip().split('\n')
            for line in lines:
                if line.strip():
                    clean_line = line.strip().replace('-', '').replace('•', '').strip()
                    if is_list:
                        current_y = self.get_y()
                        self.set_xy(12, current_y)
                        self.cell(4, 5, chr(149), 0, 0)
                        self.set_xy(16, current_y)
                        self.multi_cell(0, 5, clean_text(clean_line))
                    else:
                        self.multi_cell(0, 5, clean_text(clean_line))
        self.ln(2)

    def draw_simple_list(self, text):
        self.set_font('Times', '', 10)
        current_y = self.get_y()
        self.set_xy(12, current_y)
        self.cell(4, 5, chr(149), 0, 0)
        self.set_xy(16, current_y)
        self.multi_cell(0, 5, clean_text(text))

def build_pdf_resume(p, d):
    pdf = UltimateATSPDF('P', 'mm', 'A4')
    pdf.set_title(f"{clean_text(p['name'])} CV")
    pdf.set_author(clean_text(p['name']))
    pdf.set_creator("Professional Resume Builder")
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()

    # Header
    pdf.set_font('Times', 'B', 18)
    pdf.cell(0, 8, clean_text(p['name'].upper()), 0, 1, 'C')

    pdf.set_font('Times', '', 10)
    contact = [p['location'], p['phone'], p['email']]
    pdf.cell(0, 5, clean_text(" | ".join([x for x in contact if x])), 0, 1, 'C')

    links = [l for l in [p['linkedin'], p['github']] if l]
    if links: pdf.cell(0, 5, clean_text(" | ".join(links)), 0, 1, 'C')
    pdf.ln(5)

    if p['summary']:
        pdf.draw_section_title('Professional Summary')
        pdf.set_font('Times', '', 10)
        pdf.multi_cell(0, 5, clean_text(p['summary']))

    if d['skills']:
        pdf.draw_section_title('Technical Skills')
        for i in d['skills']: pdf.draw_simple_list(i['text'])

    if d['experience']:
        pdf.draw_section_title('Professional Experience')
        for i in d['experience']: pdf.draw_complex_item(i['title'], i['company'], i['date'], i['desc'], True)

    if d['projects']:
        pdf.draw_section_title('Technical Projects')
        for i in d['projects']: pdf.draw_complex_item(i['title'], None, i['date'], i['desc'], True)

    if d['education']:
        pdf.draw_section_title('Education')
        for i in d['education']: pdf.draw_complex_item(i['degree'], i['school'], i['date'], None, False)

    if d['certs']:
        pdf.draw_section_title('Certifications')
        for i in d['certs']: pdf.draw_complex_item(i['name'], i['authority'], i['date'], None, False)

    if d['languages']:
        pdf.draw_section_title('Languages')
        for i in d['languages']: pdf.draw_simple_list(i['text'])

    return pdf

# =============================================================================
# 7. UI COMPONENTS
# =============================================================================

def render_header():
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.markdown("""
        <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #6366F1, #EC4899);
            border-radius: 15px; display: flex; align-items: center; justify-content: center;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);">
            <span style="color: white; font-weight: 800; font-size: 24px;">AI</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown('<h1 class="gradient-text">ULTIMATE RESUME BUILDER</h1>', unsafe_allow_html=True)
        st.markdown('<p style="margin-top: -10px;">ATS-Optimized | Privacy Focused | Enterprise Grade</p>', unsafe_allow_html=True)

@st.dialog("⚠️ Validation Error")
def show_error_modal(errors):
    st.markdown("### Action Required")
    for err in errors:
        st.markdown(f"<div style='background:rgba(255,193,7,0.15); border-left:4px solid #FFC107; padding:10px; margin-bottom:5px; font-size:14px; color:#F1F5F9'>{err}</div>", unsafe_allow_html=True)
    if st.button("I Understand", type="primary"): st.rerun()

def render_section_manager(key, title, ph_t="", ph_c="", ph_d="", ph_desc=""):
    with st.container():
        st.subheader(title)
        is_edit = (st.session_state.edit_target and st.session_state.edit_target['section'] == key)
        k1, k2, k3, k4 = f"t_{key}", f"c_{key}", f"d_{key}", f"desc_{key}"

        # Inputs
        if key == 'experience':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text_input("Job Title", key=k1, placeholder=ph_t)
            c2.text_input("Company", key=k2, placeholder=ph_c)
            c3.text_input("Date", key=k3, placeholder=ph_d)
            st.text_area("Description", key=k4, height=120, placeholder=ph_desc)
        elif key == 'education':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text_input("Degree", key=k1, placeholder=ph_t)
            c2.text_input("Institution", key=k2, placeholder=ph_c)
            c3.text_input("Date", key=k3, placeholder=ph_d)
        elif key == 'projects':
            c1, c2 = st.columns([3, 1])
            c1.text_input("Project Name", key=k1, placeholder=ph_t)
            c2.text_input("Date", key=k3, placeholder=ph_d)
            st.text_area("Description", key=k4, height=120, placeholder=ph_desc)
        elif key == 'certs':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text_input("Certification Name", key=k1, placeholder=ph_t)
            c2.text_input("Issuing Authority", key=k2, placeholder=ph_c)
            c3.text_input("Date", key=k3, placeholder=ph_d)
        else:
            st.text_input("Item Name", key=k1, placeholder=ph_t)

        # Buttons
        b1, b2, _ = st.columns([1, 1, 6])
        if is_edit:
            idx = st.session_state.edit_target['index']
            b1.button("Save Changes", key=f"s_{key}", type="primary", on_click=save_changes_callback, args=(key, idx))
            b2.button("Cancel", key=f"x_{key}", kind="secondary", on_click=cancel_edit_callback, args=(key,))
        else:
            b1.button("Add Item", key=f"a_{key}", type="secondary", on_click=add_item_callback, args=(key,))

        # List
        if st.session_state[key]:
            st.markdown("---")
            for i, item in enumerate(st.session_state[key]):
                t = item.get('title') or item.get('degree') or item.get('name') or item.get('text')
                sub = item.get('company') or item.get('school') or item.get('authority')
                date = item.get('date')

                html = f"<div style='display:flex; justify-content:space-between; margin-bottom:5px;'><div><span style='color:#F8FAFC; font-weight:600;'>{i+1}. {t}</span>"
                if sub: html += f"<span style='color:#94A3B8; font-size:13px; margin-left:10px;'>| {sub}</span>"
                if date: html += f"<span style='color:#64748B; font-size:12px; margin-left:10px;'>({date})</span>"
                html += "</div></div>"

                r1, r2, r3 = st.columns([0.85, 0.07, 0.08])
                r1.markdown(html, unsafe_allow_html=True)
                r2.button("✏️", key=f"ed_{key}_{i}", on_click=trigger_edit_callback, args=(key, i))
                r3.button("🗑️", key=f"del_{key}_{i}", on_click=delete_item_callback, args=(key, i))

# =============================================================================
# 8. MAIN APP
# =============================================================================

def main():
    render_header()
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
        st.subheader("👤 Personal Information")
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Full Name", placeholder="e.g. John Doe")
        email = c2.text_input("Email", placeholder="e.g. john.doe@example.com")
        phone = c3.text_input("Phone", placeholder="e.g. +1 234 567 890")

        c4, c5, c6 = st.columns(3)
        loc = c4.text_input("Location", placeholder="City, Country")
        linkedin = c5.text_input("LinkedIn URL", placeholder="linkedin.com/in/johndoe")
        github = c6.text_input("GitHub URL", placeholder="github.com/johndoe")

        st.markdown("<br>", unsafe_allow_html=True)
        summary = st.text_area("Professional Summary", height=100,
                               placeholder="Experienced Software Engineer with a focus on...",
                               help="Keep it brief (2-4 sentences).")
        st.caption(f"Characters: {len(summary)} / {MAX_SUMMARY_CHARS}")

    st.markdown("<br>", unsafe_allow_html=True)

    render_section_manager('experience', 'Professional Experience',
                           ph_t="Job Title (e.g. Senior Developer)",
                           ph_c="Company Name", ph_d="Jan 2020 - Present",
                           ph_desc="• Led a team of 5 developers...\n• Improved performance by 30%...")

    render_section_manager('projects', 'Technical Projects',
                           ph_t="Project Name", ph_d="2024",
                           ph_desc="• Built using Python and AWS...\n• Solved scalability issues...")

    render_section_manager('education', 'Education',
                           ph_t="Degree (e.g. B.Sc. Computer Science)",
                           ph_c="University Name", ph_d="2018 - 2022")

    render_section_manager('skills', 'Technical Skills', ph_t="e.g. Python, SQL, Docker (One per line or separate items)")
    render_section_manager('certs', 'Certifications', ph_t="Certificate Name", ph_c="Issuing Org", ph_d="2023")
    render_section_manager('languages', 'Languages', ph_t="Language (e.g. English: Native)")

    st.divider()

    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        if st.button("🚀 GENERATE PDF RESUME", type="primary", use_container_width=True):
            errors = []
            if not name.strip(): errors.append("Full Name is required.")
            if not email.strip(): errors.append("Email is required.")
            elif not validate_email(email): errors.append("Invalid Email Format.")

            if not st.session_state.experience and not st.session_state.education:
                errors.append("Please add at least one Experience or Education entry.")

            if errors:
                show_error_modal(errors)
            else:
                try:
                    p_data = {'name': name, 'email': email, 'phone': phone, 'location': loc, 'linkedin': linkedin, 'github': github, 'summary': summary}
                    l_data = {k: st.session_state[k] for k in SECTIONS}

                    pdf = build_pdf_resume(p_data, l_data)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        pdf.output(tmp.name)
                        with open(tmp.name, "rb") as f:
                            st.balloons()
                            st.toast("Resume Generated Successfully!", icon="🎉")
                            st.download_button("📥 DOWNLOAD PDF", f, f"{name.replace(' ', '_')}_Resume.pdf", "application/pdf", type="primary")
                    os.unlink(tmp.name)
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()