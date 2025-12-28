import streamlit as st
from fpdf import FPDF
import tempfile
import os

# --- 1. Page Configuration (Modern Dark Theme) ---
st.set_page_config(
    page_title="Resume AI Builder",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. Custom CSS for "Outlier AI" Look ---
st.markdown("""
<style>
    /* General App Styling */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Inter', sans-serif;
    }

    /* Input Fields */
    .stTextInput input, .stTextArea textarea {
        background-color: #262730;
        color: #ffffff;
        border: 1px solid #41444C;
        border-radius: 8px;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #4F8BF9;
        box-shadow: 0 0 0 1px #4F8BF9;
    }

    /* Buttons */
    .stButton button {
        background-color: #4F8BF9;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        background-color: #3a75d9;
        transform: translateY(-1px);
    }

    /* Secondary/Delete Buttons */
    button[kind="secondary"] {
        background-color: transparent;
        border: 1px solid #FF4B4B;
        color: #FF4B4B;
    }
    button[kind="secondary"]:hover {
        background-color: #FF4B4B22;
        border-color: #FF4B4B;
        color: #FF4B4B;
    }

    /* Cards/Containers */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: #161920;
        border: 1px solid #30333D;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }

    /* Typography */
    h1, h2, h3 {
        color: #FFFFFF;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .block-container {
        padding-top: 3rem;
        max-width: 900px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Session State Initialization ---
keys = ['experience', 'projects', 'education', 'certs', 'skills', 'languages']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = []
if 'edit_target' not in st.session_state:
    st.session_state.edit_target = None


# --- 4. PDF Logic (Robust) ---
def clean_text(text):
    if text:
        return text.encode('latin-1', 'replace').decode('latin-1')
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


def generate_pdf(personal, data):
    pdf = PDF('P', 'mm', 'A4')
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()

    # Header
    pdf.set_font('Times', 'B', 18)
    pdf.cell(0, 8, clean_text(personal['name'].upper()), 0, 1, 'C')
    pdf.set_font('Times', '', 11)
    pdf.cell(0, 6, clean_text(f"{personal['location']} | {personal['phone']} | {personal['email']}"), 0, 1, 'C')
    links = [l for l in [personal['linkedin'], personal['github']] if l]
    if links: pdf.cell(0, 6, " | ".join([clean_text(l) for l in links]), 0, 1, 'C')
    pdf.ln(6)

    if personal['summary']:
        pdf.section_title('Professional Summary')
        pdf.set_font('Times', '', 11)
        pdf.multi_cell(0, 5, clean_text(personal['summary']))

    sections = [
        ('Technical Skills', 'skills', False),
        ('Professional Experience', 'experience', True),
        ('Technical Projects', 'projects', True),
        ('Education', 'education', False),
        ('Certifications', 'certs', False),
        ('Languages', 'languages', False)
    ]

    for title, key, is_bullet in sections:
        if data[key]:
            pdf.section_title(title)
            for item in data[key]:
                if key in ['experience', 'projects']:
                    pdf.add_item(item['title'], item['desc'], True)
                elif key == 'education':
                    pdf.add_item(item['degree'], item['details'])
                elif key == 'certs':
                    pdf.add_item(item['name'], item['auth'])
                elif key in ['skills', 'languages']:
                    # Skills as bullet list
                    pdf.set_font('Times', '', 11)
                    y = pdf.get_y()
                    pdf.set_xy(12, y)
                    pdf.cell(5, 5, chr(149), 0, 0)
                    pdf.set_xy(17, y)
                    pdf.multi_cell(0, 5, clean_text(item['text']))
    return pdf


# --- 5. UI Components (Section Manager) ---
def render_section(key, title, input_label_1, input_label_2=None):
    # Card Container
    with st.container(border=True):
        c_head, c_count = st.columns([0.9, 0.1])
        c_head.markdown(f"### {title}")
        c_count.markdown(f"**{len(st.session_state[key])}** Items")

        # Check Edit Mode
        is_editing = (st.session_state.edit_target and st.session_state.edit_target['section'] == key)
        edit_idx = st.session_state.edit_target['index'] if is_editing else None

        # Defaults
        val1, val2 = "", ""
        if is_editing:
            item = st.session_state[key][edit_idx]
            if key in ['experience', 'projects']:
                val1, val2 = item['title'], item['desc']
            elif key == 'education':
                val1, val2 = item['degree'], item['details']
            elif key == 'certs':
                val1, val2 = item['name'], item['auth']
            else:
                val1 = item['text']

        # Inputs Grid
        col1, col2 = st.columns([1, 2] if input_label_2 else [1, 0.01])
        new_val1 = col1.text_input(input_label_1, value=val1, key=f"in_{key}_1", placeholder="Type here...")
        new_val2 = ""
        if input_label_2:
            new_val2 = col2.text_area(input_label_2, value=val2, height=100, key=f"in_{key}_2",
                                      placeholder="Details...")

        # Action Buttons
        b1, b2, _ = st.columns([1, 1, 3])
        if is_editing:
            if b1.button("Save Changes", key=f"save_{key}", type="primary"):
                obj = {}
                if key in ['experience', 'projects']:
                    obj = {'title': new_val1, 'desc': new_val2}
                elif key == 'education':
                    obj = {'degree': new_val1, 'details': new_val2}
                elif key == 'certs':
                    obj = {'name': new_val1, 'auth': new_val2}
                else:
                    obj = {'text': new_val1}
                st.session_state[key][edit_idx] = obj
                st.session_state.edit_target = None
                st.rerun()
            if b2.button("Cancel", key=f"cancel_{key}"):
                st.session_state.edit_target = None
                st.rerun()
        else:
            if b1.button("Add Item", key=f"add_{key}"):
                if new_val1:
                    obj = {}
                    if key in ['experience', 'projects']:
                        obj = {'title': new_val1, 'desc': new_val2}
                    elif key == 'education':
                        obj = {'degree': new_val1, 'details': new_val2}
                    elif key == 'certs':
                        obj = {'name': new_val1, 'auth': new_val2}
                    else:
                        obj = {'text': new_val1}
                    st.session_state[key].append(obj)
                    st.rerun()

        # List Display (Minimalist)
        if st.session_state[key]:
            st.markdown("---")
            for i, item in enumerate(st.session_state[key]):
                # Get Title for Display
                if key in ['experience', 'projects']:
                    txt = item['title']
                elif key == 'education':
                    txt = item['degree']
                elif key == 'certs':
                    txt = item['name']
                else:
                    txt = item['text']

                r1, r2, r3 = st.columns([0.8, 0.1, 0.1])
                r1.markdown(f"**{i + 1}. {txt}**")
                if r2.button("✎", key=f"ed_{key}_{i}"):
                    st.session_state.edit_target = {'section': key, 'index': i}
                    st.rerun()
                if r3.button("✖", key=f"del_{key}_{i}"):
                    st.session_state[key].pop(i)
                    if is_editing and edit_idx == i: st.session_state.edit_target = None
                    st.rerun()


# --- 6. Main Layout ---

st.title("⚡ Resume AI Builder")
st.markdown("Professional, ATS-friendly resumes in seconds.")

# Personal Info Card
with st.container(border=True):
    st.subheader("👤 Personal Details")
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Full Name", "Saif Eldien Yehia")
    email = c2.text_input("Email")
    phone = c3.text_input("Phone")

    c4, c5, c6 = st.columns(3)
    loc = c4.text_input("Location")
    link = c5.text_input("LinkedIn URL")
    git = c6.text_input("GitHub URL")

    summ = st.text_area("Professional Summary", height=80, placeholder="Briefly describe your career highlights...")

# Sections
render_section('experience', 'Professional Experience', 'Job Title | Company | Date', 'Description (Bullets)')
render_section('projects', 'Technical Projects', 'Project Name', 'Description (Bullets)')
render_section('education', 'Education', 'Degree', 'Institution | Date')
render_section('skills', 'Technical Skills', 'Skill (e.g. Python, SQL)')
render_section('certs', 'Certifications', 'Certification Name', 'Authority / Date')
render_section('languages', 'Languages', 'Language (e.g. English: C1)')

# Generate Action
st.divider()
col_gen, _ = st.columns([1, 2])
if col_gen.button("🚀 GENERATE PDF RESUME", type="primary", use_container_width=True):
    if not name:
        st.error("Full Name is required!")
    else:
        p_data = {'name': name, 'email': email, 'phone': phone, 'location': loc, 'linkedin': link, 'github': git,
                  'summary': summ}
        l_data = {k: st.session_state[k] for k in keys}

        try:
            pdf = generate_pdf(p_data, l_data)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                with open(tmp.name, "rb") as f:
                    st.success("Resume built successfully!")
                    st.download_button("📥 Download PDF", f, f"{name.replace(' ', '_')}_Resume.pdf", "application/pdf")
            os.unlink(tmp.name)
        except Exception as e:
            st.error(f"Error: {e}")