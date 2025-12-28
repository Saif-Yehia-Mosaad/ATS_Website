"""
=============================================================================
PROJECT: ULTIMATE ATS RESUME BUILDER (PRO EDITION)
AUTHOR: SAIF ELDIEN (Generated via AI Assistant)
VERSION: 5.0.0 (Production Ready)
DESCRIPTION:
    A robust, privacy-focused, ATS-optimized resume builder using Streamlit.
    Features include:
    - Outlier AI Glassmorphism UI Theme.
    - Session State Management with Callbacks (Crash-free).
    - Advanced FPDF Engine with Linear Parsing logic for ATS.
    - Input Validation & Sanitization.
    - Dynamic Placeholders & Help Tooltips.
=============================================================================
"""

import streamlit as st
from fpdf import FPDF
import tempfile
import os
import re
from datetime import datetime

# =============================================================================
# 1. APP CONFIGURATION & CONSTANTS
# =============================================================================

st.set_page_config(
    page_title="Saif's Professional Resume Builder",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Constants for Validation & Limits
MAX_SUMMARY_CHARS = 2000
SECTIONS = ['experience', 'projects', 'education', 'certs', 'skills', 'languages']


# =============================================================================
# 2. ADVANCED CSS STYLING (OUTLIER AI THEME)
# =============================================================================

def load_css():
    st.markdown("""
    <style>
        /* --- GLOBAL THEME --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: rgb(15,23,42);
            background: linear-gradient(170deg, rgba(15,23,42,1) 0%, rgba(30,27,75,1) 40%, rgba(15,23,42,1) 100%);
            color: #F8FAFC;
        }

        /* --- GLASSMORPHISM CARDS --- */
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            transition: transform 0.2s ease-in-out;
        }

        /* Hover Effect on Cards (Subtle) */
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"]:hover {
            border-color: rgba(99, 102, 241, 0.3);
        }

        /* --- INPUT FIELDS --- */
        .stTextInput input, .stTextArea textarea {
            background-color: #0F172A !important;
            border: 1px solid #334155 !important;
            color: #F8FAFC !important;
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 14px;
            transition: all 0.2s;
        }

        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #818CF8 !important;
            box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.2);
            outline: none;
        }

        /* --- BUTTONS --- */
        /* Primary (Gradient) */
        .stButton button[kind="primary"] {
            background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
            color: white;
            border: none;
            padding: 10px 28px;
            border-radius: 8px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            font-size: 13px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: all 0.2s;
        }
        .stButton button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4);
        }

        /* Secondary (Outline) */
        .stButton button[kind="secondary"] {
            background: transparent;
            border: 1px solid #475569;
            color: #94A3B8;
            border-radius: 8px;
            font-weight: 500;
        }
        .stButton button[kind="secondary"]:hover {
            border-color: #E2E8F0;
            color: #E2E8F0;
            background-color: rgba(255,255,255,0.05);
        }

        /* --- TYPOGRAPHY --- */
        h1, h2, h3, h4, h5, h6 {
            color: #F8FAFC !important;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        p, label, span, div {
            color: #CBD5E1 !important;
        }

        /* Helper/Tooltip Text */
        .stMarkdown div p {
            font-size: 14px;
            opacity: 0.9;
        }

        /* --- TOAST NOTIFICATIONS --- */
        .stToast {
            background-color: #1E293B !important;
            color: white !important;
            border: 1px solid #475569;
            border-radius: 8px;
        }

        /* --- CUSTOM HEADER GRADIENT TEXT --- */
        .gradient-text {
            background: -webkit-linear-gradient(45deg, #2DD4BF, #8B5CF6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
    </style>
    """, unsafe_allow_html=True)


load_css()


# =============================================================================
# 3. UTILITIES & VALIDATION
# =============================================================================

def clean_text(text: str) -> str:
    """
    Sanitizes text to ensure PDF compatibility (Latin-1 encoding).
    Replaces smart quotes, dashes, and other non-standard chars.
    """
    if not text:
        return ""

    replacements = {
        '–': '-', '—': '-',
        '“': '"', '”': '"',
        '’': "'", '‘': "'",
        '…': '...',
        '•': '-'  # Bullets handled manually in PDF engine
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Final safety encoding
    return text.encode('latin-1', 'replace').decode('latin-1')


def validate_email(email: str) -> bool:
    """Checks if the email format is valid using Regex."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


# =============================================================================
# 4. SESSION STATE MANAGER
# =============================================================================

# Initialize Session State with Empty Lists (PRIVACY FOCUSED - NO DEFAULT DATA)
for key in SECTIONS:
    if key not in st.session_state:
        st.session_state[key] = []

if 'edit_target' not in st.session_state:
    st.session_state.edit_target = None


# =============================================================================
# 5. CALLBACK FUNCTIONS (STABILITY LAYER)
# =============================================================================
# Using callbacks prevents Streamlit form crashing by updating state *before* re-run.

def add_item_callback(section_key):
    # Retrieve values from widget state keys
    t_key, c_key, d_key, desc_key = f"t_{section_key}", f"c_{section_key}", f"d_{section_key}", f"desc_{section_key}"

    v1 = st.session_state.get(t_key, "").strip()
    v2 = st.session_state.get(c_key, "").strip()
    v3 = st.session_state.get(d_key, "").strip()
    v4 = st.session_state.get(desc_key, "").strip()

    valid_entry = False
    new_item = {}

    # Logic to build item dict based on section type
    if section_key == 'experience' and v1:
        new_item = {'title': v1, 'company': v2, 'date': v3, 'desc': v4}
        valid_entry = True
    elif section_key == 'education' and v1:
        new_item = {'degree': v1, 'school': v2, 'date': v3}
        valid_entry = True
    elif section_key == 'projects' and v1:
        new_item = {'title': v1, 'date': v3, 'desc': v4}
        valid_entry = True
    elif section_key == 'certs' and v1:
        new_item = {'name': v1, 'authority': v2, 'date': v3}
        valid_entry = True
    elif section_key in ['skills', 'languages'] and v1:
        new_item = {'text': v1}
        valid_entry = True

    if valid_entry:
        st.session_state[section_key].append(new_item)
        # Clear inputs securely
        for k in [t_key, c_key, d_key, desc_key]:
            if k in st.session_state: st.session_state[k] = ""
        st.toast(f"✅ Added to {section_key.capitalize()}")
    else:
        st.toast("⚠️ Main Title field is required!", icon="🚨")


def save_changes_callback(section_key, idx):
    t_key, c_key, d_key, desc_key = f"t_{section_key}", f"c_{section_key}", f"d_{section_key}", f"desc_{section_key}"
    v1 = st.session_state.get(t_key, "").strip()
    v2 = st.session_state.get(c_key, "").strip()
    v3 = st.session_state.get(d_key, "").strip()
    v4 = st.session_state.get(desc_key, "").strip()

    new_item = {}
    if section_key == 'experience':
        new_item = {'title': v1, 'company': v2, 'date': v3, 'desc': v4}
    elif section_key == 'education':
        new_item = {'degree': v1, 'school': v2, 'date': v3}
    elif section_key == 'projects':
        new_item = {'title': v1, 'date': v3, 'desc': v4}
    elif section_key == 'certs':
        new_item = {'name': v1, 'authority': v2, 'date': v3}
    else:
        new_item = {'text': v1}

    st.session_state[section_key][idx] = new_item
    st.session_state.edit_target = None  # Exit edit mode

    # Clear inputs
    for k in [t_key, c_key, d_key, desc_key]:
        if k in st.session_state: st.session_state[k] = ""
    st.toast("💾 Changes Saved Successfully")


def cancel_edit_callback(section_key):
    st.session_state.edit_target = None
    # Clear inputs
    t_key, c_key, d_key, desc_key = f"t_{section_key}", f"c_{section_key}", f"d_{section_key}", f"desc_{section_key}"
    for k in [t_key, c_key, d_key, desc_key]:
        if k in st.session_state: st.session_state[k] = ""


def delete_item_callback(section_key, idx):
    st.session_state[section_key].pop(idx)
    # If we were editing the item we just deleted, cancel edit mode
    if st.session_state.edit_target and \
            st.session_state.edit_target['section'] == section_key and \
            st.session_state.edit_target['index'] == idx:
        st.session_state.edit_target = None
    st.toast("🗑️ Item Deleted")


def trigger_edit_callback(section_key, idx):
    """Populates the input fields with the existing data for editing."""
    st.session_state.edit_target = {'section': section_key, 'index': idx}
    item = st.session_state[section_key][idx]

    # Map item values to widget keys based on section type
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
# 6. ATS PDF GENERATION ENGINE
# =============================================================================

class UltimateATSPDF(FPDF):
    """
    Custom PDF Class designed specifically for ATS Parsing.
    - Uses Standard Fonts (Times)
    - Linear Layout (Top to Bottom)
    - Metadata Injection
    """

    def header(self):
        # No graphical header to confuse ATS
        pass

    def footer(self):
        # Simple footer with page number
        self.set_y(-15)
        self.set_font('Times', '', 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def draw_section_title(self, title):
        """Draws a section header with a clean separator line."""
        self.ln(6)
        self.set_font('Times', 'B', 11)
        self.set_text_color(0, 0, 0)  # Black
        self.cell(0, 6, title.upper(), 0, 1, 'L')
        self.set_draw_color(0, 0, 0)  # Black Line
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def draw_complex_item(self, title, subtitle, date, description, is_list=True):
        """
        Renders an item with Title (Left), Date (Right), Subtitle (Left), and Description.
        This layout is optimized for parsing logic.
        """
        # Line 1: Title & Date
        self.set_font('Times', 'B', 10)
        self.set_text_color(0, 0, 0)

        # Calculate width to prevent overlapping
        title_w = 140 if date else 190

        # Draw Title
        self.cell(title_w, 5, clean_text(title), 0, 0, 'L')

        # Draw Date (Aligned Right)
        if date:
            self.set_font('Times', '', 10)
            self.cell(0, 5, clean_text(date), 0, 1, 'R')
        else:
            self.ln(5)  # Just finish the line

        # Line 2: Subtitle (Company / Institution)
        if subtitle:
            self.set_font('Times', 'I', 10)  # Italics for distinction
            self.cell(0, 5, clean_text(subtitle), 0, 1, 'L')

        # Line 3: Description (Bullets)
        if description:
            self.set_font('Times', '', 10)
            lines = description.strip().split('\n')
            for line in lines:
                if line.strip():
                    # Manual Bullet Point Drawing for consistency
                    clean_line = line.strip().replace('-', '').replace('•', '').strip()

                    if is_list:
                        current_y = self.get_y()
                        self.set_xy(12, current_y)  # Indent
                        self.cell(4, 5, chr(149), 0, 0)  # Bullet Char
                        self.set_xy(16, current_y)
                        self.multi_cell(0, 5, clean_text(clean_line))
                    else:
                        self.multi_cell(0, 5, clean_text(clean_line))

        self.ln(2)  # Spacing after item

    def draw_simple_list(self, text):
        """Renders simple bullet points (Skills / Languages)."""
        self.set_font('Times', '', 10)
        current_y = self.get_y()
        self.set_xy(12, current_y)
        self.cell(4, 5, chr(149), 0, 0)
        self.set_xy(16, current_y)
        self.multi_cell(0, 5, clean_text(text))


def build_pdf_resume(personal_info, sections_data):
    """Orchestrates the PDF creation process."""

    pdf = UltimateATSPDF(orientation='P', unit='mm', format='A4')

    # ATS Metadata Injection
    pdf.set_title(f"{clean_text(personal_info['name'])} Resume")
    pdf.set_author(clean_text(personal_info['name']))
    pdf.set_creator("Saif's Ultimate Resume Builder")
    pdf.set_keywords("Resume, CV, ATS, Software Engineer, Developer")

    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # --- 1. HEADER (Contact Info) ---
    pdf.set_font('Times', 'B', 18)
    pdf.cell(0, 8, clean_text(personal_info['name'].upper()), 0, 1, 'C')

    pdf.set_font('Times', '', 10)

    # Smart joining of contact info to avoid empty pipes
    contact_list = [
        personal_info['location'],
        personal_info['phone'],
        personal_info['email']
    ]
    contact_string = " | ".join([c for c in contact_list if c])
    pdf.cell(0, 5, clean_text(contact_string), 0, 1, 'C')

    # Links
    links_list = [
        personal_info['linkedin'],
        personal_info['github']
    ]
    links_string = " | ".join([l for l in links_list if l])
    if links_string:
        pdf.cell(0, 5, clean_text(links_string), 0, 1, 'C')

    pdf.ln(5)

    # --- 2. SUMMARY ---
    if personal_info['summary']:
        pdf.draw_section_title('Professional Summary')
        pdf.set_font('Times', '', 10)
        pdf.multi_cell(0, 5, clean_text(personal_info['summary']))

    # --- 3. SECTIONS ITERATION ---
    # Defined order for best ATS results

    # Skills first (High relevance)
    if sections_data['skills']:
        pdf.draw_section_title('Technical Skills')
        for item in sections_data['skills']:
            pdf.draw_simple_list(item['text'])

    # Experience
    if sections_data['experience']:
        pdf.draw_section_title('Professional Experience')
        for item in sections_data['experience']:
            pdf.draw_complex_item(item['title'], item['company'], item['date'], item['desc'], is_list=True)

    # Projects
    if sections_data['projects']:
        pdf.draw_section_title('Technical Projects')
        for item in sections_data['projects']:
            pdf.draw_complex_item(item['title'], None, item['date'], item['desc'], is_list=True)

    # Education
    if sections_data['education']:
        pdf.draw_section_title('Education')
        for item in sections_data['education']:
            pdf.draw_complex_item(item['degree'], item['school'], item['date'], None, is_list=False)

    # Certifications
    if sections_data['certs']:
        pdf.draw_section_title('Certifications')
        for item in sections_data['certs']:
            pdf.draw_complex_item(item['name'], item['authority'], item['date'], None, is_list=False)

    # Languages
    if sections_data['languages']:
        pdf.draw_section_title('Languages')
        for item in sections_data['languages']:
            pdf.draw_simple_list(item['text'])

    return pdf


# =============================================================================
# 7. UI COMPONENT RENDERERS
# =============================================================================

def render_header():
    """Renders the top banner with Logo and Title."""
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.markdown("""
        <div style="
            width: 60px; height: 60px;
            background: linear-gradient(135deg, #6366F1, #EC4899);
            border-radius: 15px;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        ">
            <span style="color: white; font-weight: 800; font-size: 24px;">AI</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown('<h1 class="gradient-text">ULTIMATE RESUME BUILDER</h1>', unsafe_allow_html=True)
        st.markdown('<p style="margin-top: -10px;">ATS-Optimized Structure | Privacy Focused | Enterprise Grade</p>',
                    unsafe_allow_html=True)


@st.dialog("⚠️ Resume Validation")
def show_error_modal(errors):
    """Displays a professional modal dialog for validation errors."""
    st.markdown("### Action Required")
    st.markdown("Please fix the following issues to ensure your resume generates correctly:")

    for err in errors:
        st.markdown(f"""
        <div style="
            background-color: rgba(255, 193, 7, 0.15);
            border-left: 4px solid #FFC107;
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 4px;
        ">
            <span style="color: #F1F5F9; font-size: 14px;">{err}</span>
        </div>
        """, unsafe_allow_html=True)

    if st.button("I Understand", type="primary"):
        st.rerun()


def render_section_manager(key, title, ph_t="", ph_c="", ph_d="", ph_desc=""):
    """
    Generic function to render Add/Edit/List UI for any section.
    Includes placeholders logic and edit mode handling.
    """
    with st.container():
        st.subheader(title)

        # Check if we are editing THIS specific section
        is_edit_mode = (st.session_state.edit_target and st.session_state.edit_target['section'] == key)

        # Keys for widgets
        k1, k2, k3, k4 = f"t_{key}", f"c_{key}", f"d_{key}", f"desc_{key}"

        # --- INPUT FORM ---
        # Layout depends on section type
        if key == 'experience':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text_input("Job Title", key=k1, placeholder=ph_t)
            c2.text_input("Company", key=k2, placeholder=ph_c)
            c3.text_input("Date", key=k3, placeholder=ph_d)
            st.text_area("Description (Bullet Points)", key=k4, height=120, placeholder=ph_desc,
                         help="Use bullet points for better ATS parsing.")

        elif key == 'education':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text_input("Degree", key=k1, placeholder=ph_t)
            c2.text_input("Institution", key=k2, placeholder=ph_c)
            c3.text_input("Date", key=k3, placeholder=ph_d)

        elif key == 'projects':
            c1, c2 = st.columns([3, 1])
            c1.text_input("Project Name", key=k1, placeholder=ph_t)
            c2.text_input("Date", key=k3, placeholder=ph_d)
            st.text_area("Description (Bullet Points)", key=k4, height=120, placeholder=ph_desc)

        elif key == 'certs':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text_input("Certification Name", key=k1, placeholder=ph_t)
            c2.text_input("Issuing Authority", key=k2, placeholder=ph_c)
            c3.text_input("Date", key=k3, placeholder=ph_d)

        else:  # Skills & Languages
            st.text_input("Item Name", key=k1, placeholder=ph_t)

        # --- ACTION BUTTONS ---
        btn_col1, btn_col2, _ = st.columns([1, 1, 6])

        if is_edit_mode:
            idx = st.session_state.edit_target['index']
            # Save Button
            btn_col1.button("Save Changes", key=f"save_{key}", type="primary",
                            on_click=save_changes_callback, args=(key, idx))
            # Cancel Button
            btn_col2.button("Cancel", key=f"cancel_{key}", kind="secondary",
                            on_click=cancel_edit_callback, args=(key,))
        else:
            # Add Button
            btn_col1.button("Add Item", key=f"add_{key}", type="secondary",
                            on_click=add_item_callback, args=(key,))

        # --- LIST VIEW (ITEMS) ---
        if st.session_state[key]:
            st.markdown("---")
            for i, item in enumerate(st.session_state[key]):
                # Formatting Display Logic
                main_txt = item.get('title') or item.get('degree') or item.get('name') or item.get('text')
                sub_txt = item.get('company') or item.get('school') or item.get('authority')
                date_txt = item.get('date')

                # HTML Construction for beautiful list items
                html_block = f"""
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <div>
                        <span style="color: #F8FAFC; font-weight: 600; font-size: 15px;">{i + 1}. {main_txt}</span>
                        {f'<span style="color: #94A3B8; font-size: 13px; margin-left: 10px;">| {sub_txt}</span>' if sub_txt else ''}
                        {f'<span style="color: #64748B; font-size: 12px; margin-left: 10px;">({date_txt})</span>' if date_txt else ''}
                    </div>
                </div>
                """

                r1, r2, r3 = st.columns([0.85, 0.07, 0.08])
                r1.markdown(html_block, unsafe_allow_html=True)

                # Edit / Delete Buttons with Callbacks
                r2.button("✏️", key=f"edt_{key}_{i}", help="Edit Item",
                          on_click=trigger_edit_callback, args=(key, i))
                r3.button("🗑️", key=f"del_{key}_{i}", help="Delete Item",
                          on_click=delete_item_callback, args=(key, i))


# =============================================================================
# 8. MAIN APPLICATION LAYOUT
# =============================================================================

def main():
    render_header()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- IDENTITY SECTION ---
    with st.container():
        st.subheader("👤 Personal Information")
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Full Name", placeholder="e.g. Saif Eldien")
        email = c2.text_input("Email", placeholder="e.g. saif@example.com")
        phone = c3.text_input("Phone", placeholder="e.g. +20 123 456 7890")

        c4, c5, c6 = st.columns(3)
        loc = c4.text_input("Location", placeholder="City, Country")
        linkedin = c5.text_input("LinkedIn URL", placeholder="linkedin.com/in/...")
        github = c6.text_input("GitHub URL", placeholder="github.com/...")

        st.markdown("<br>", unsafe_allow_html=True)
        summary = st.text_area("Professional Summary", height=100,
                               placeholder="Briefly describe your experience, key skills, and career goals...",
                               help="Keep it between 2-4 sentences for best ATS results.")

        # Summary Character Count
        st.caption(f"Characters: {len(summary)} / {MAX_SUMMARY_CHARS}")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- CONTENT SECTIONS ---
    # We pass explicit placeholders to guide the user towards high-scoring content

    render_section_manager('experience', 'Professional Experience',
                           ph_t="Job Title (e.g. Backend Developer)",
                           ph_c="Company Name",
                           ph_d="Jan 2023 - Present",
                           ph_desc="• Achieved [X]% improvement in...\n• Led the development of...")

    render_section_manager('projects', 'Technical Projects',
                           ph_t="Project Name",
                           ph_d="2024",
                           ph_desc="• Built using Python, Streamlit...\n• Solved [Problem] by implementing [Solution]...")

    render_section_manager('education', 'Education',
                           ph_t="Degree (e.g. B.Sc. Computer Science)",
                           ph_c="University Name",
                           ph_d="2020 - 2024")

    render_section_manager('skills', 'Technical Skills',
                           ph_t="e.g. Python, SQL, Docker, AWS (Add one by one)")

    render_section_manager('certs', 'Certifications',
                           ph_t="Certificate Name",
                           ph_c="Issuing Organization",
                           ph_d="Issued Date")

    render_section_manager('languages', 'Languages',
                           ph_t="Language (e.g. English: Fluent)")

    st.divider()

    # --- GENERATION LOGIC ---
    col_gen_1, col_gen_2, col_gen_3 = st.columns([1, 2, 1])

    with col_gen_2:
        if st.button("🚀 GENERATE FINAL PDF RESUME", type="primary", use_container_width=True):

            # 1. Validation Phase
            errors = []
            if not name.strip(): errors.append("Full Name is missing.")
            if not email.strip():
                errors.append("Email is missing.")
            elif not validate_email(email):
                errors.append("Email format is invalid.")

            # Check for at least one core section
            if not st.session_state.experience and not st.session_state.education:
                errors.append("Resume looks empty! Please add Experience or Education.")

            # 2. Execution Phase
            if errors:
                show_error_modal(errors)
            else:
                try:
                    # Package Data
                    personal_data = {
                        'name': name, 'email': email, 'phone': phone,
                        'location': loc, 'linkedin': linkedin, 'github': github,
                        'summary': summary
                    }

                    sections_data = {k: st.session_state[k] for k in SECTIONS}

                    # Generate PDF
                    pdf = build_pdf_resume(personal_data, sections_data)

                    # Handle File Output
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        pdf.output(tmp_file.name)

                        with open(tmp_file.name, "rb") as f:
                            pdf_data = f.read()

                            st.balloons()  # Success Effect
                            st.toast("Resume Generated Successfully! Ready to Download.", icon="🎉")

                            st.download_button(
                                label="📥 CLICK TO DOWNLOAD PDF",
                                data=pdf_data,
                                file_name=f"{name.replace(' ', '_')}_Resume.pdf",
                                mime="application/pdf",
                                type="primary"  # Prominent download button
                            )

                    # Cleanup
                    os.unlink(tmp_file.name)

                except Exception as e:
                    st.error(f"Critical System Error: {str(e)}")
                    # In production, you would log this error to a file/service


if __name__ == "__main__":
    main()