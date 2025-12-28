import streamlit as st
from fpdf import FPDF
import tempfile
import os

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Resume AI Builder",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS Styling (Professional Dark Theme) ---
st.markdown("""
<style>
    /* Background */
    .stApp {
        background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Card Styling (Glassmorphism) */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 24px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }

    /* Input Fields */
    .stTextInput input, .stTextArea textarea {
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        color: #E2E8F0 !important;
        border-radius: 6px;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }

    /* Primary Buttons */
    .stButton button[kind="primary"] {
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        padding: 8px 20px;
        border-radius: 6px;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 13px;
        transition: all 0.2s;
    }
    .stButton button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
    }

    /* Secondary Buttons */
    .stButton button[kind="secondary"] {
        background: transparent;
        border: 1px solid #475569;
        color: #94A3B8;
        border-radius: 6px;
        font-size: 13px;
    }
    .stButton button[kind="secondary"]:hover {
        border-color: #E2E8F0;
        color: #E2E8F0;
    }

    /* Typography */
    h1, h2, h3, h4 { color: #F8FAFC !important; font-weight: 600; }
    p, label, span, div { color: #E2E8F0 !important; }
    .stToast { background-color: #1E293B !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. Session State Initialization ---
KEYS = ['experience', 'projects', 'education', 'certs', 'skills', 'languages']
for key in KEYS:
    if key not in st.session_state:
        st.session_state[key] = []
if 'edit_target' not in st.session_state:
    st.session_state.edit_target = None


# --- 4. Logic Helper Functions ---
def clean_text(text):
    """Encodes text to Latin-1 to avoid PDF errors with unsupported characters."""
    if text:
        return text.encode('latin-1', 'replace').decode('latin-1')
    return ""


# --- 5. CALLBACKS (The Core Stability Fix) ---
# These functions handle state changes cleanly to prevent Streamlit crashes.

def add_item_callback(section_key):
    # Keys for input fields
    k1, k2, k3, k4 = f"t_{section_key}", f"c_{section_key}", f"d_{section_key}", f"desc_{section_key}"

    # Get values safely
    v1 = st.session_state.get(k1, "").strip()
    v2 = st.session_state.get(k2, "").strip()
    v3 = st.session_state.get(k3, "").strip()
    v4 = st.session_state.get(k4, "").strip()

    # Validation logic
    valid = False
    new_item = {}

    if section_key == 'experience' and v1:
        new_item = {'title': v1, 'company': v2, 'date': v3, 'desc': v4};
        valid = True
    elif section_key == 'education' and v1:
        new_item = {'degree': v1, 'school': v2, 'date': v3};
        valid = True
    elif section_key == 'projects' and v1:
        new_item = {'title': v1, 'date': v3, 'desc': v4};
        valid = True
    elif section_key == 'certs' and v1:
        new_item = {'name': v1, 'authority': v2, 'date': v3};
        valid = True
    elif section_key in ['skills', 'languages'] and v1:
        new_item = {'text': v1};
        valid = True

    if valid:
        st.session_state[section_key].append(new_item)
        # Clear inputs
        for k in [k1, k2, k3, k4]:
            if k in st.session_state: st.session_state[k] = ""
        st.toast(f"Added to {section_key}", icon="✅")
    else:
        st.toast("⚠️ Main field cannot be empty!", icon="❌")


def save_changes_callback(section_key, index):
    k1, k2, k3, k4 = f"t_{section_key}", f"c_{section_key}", f"d_{section_key}", f"desc_{section_key}"
    v1 = st.session_state.get(k1, "").strip()
    v2 = st.session_state.get(k2, "").strip()
    v3 = st.session_state.get(k3, "").strip()
    v4 = st.session_state.get(k4, "").strip()

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

    st.session_state[section_key][index] = new_item
    st.session_state.edit_target = None

    # Clear inputs
    for k in [k1, k2, k3, k4]:
        if k in st.session_state: st.session_state[k] = ""
    st.toast("Changes saved successfully!", icon="💾")


def cancel_edit_callback(section_key):
    st.session_state.edit_target = None
    k1, k2, k3, k4 = f"t_{section_key}", f"c_{section_key}", f"d_{section_key}", f"desc_{section_key}"
    for k in [k1, k2, k3, k4]:
        if k in st.session_state: st.session_state[k] = ""


def delete_item_callback(section_key, index):
    st.session_state[section_key].pop(index)
    # If editing the deleted item, cancel edit
    if st.session_state.edit_target and st.session_state.edit_target['section'] == section_key and \
            st.session_state.edit_target['index'] == index:
        st.session_state.edit_target = None
    st.toast("Item deleted", icon="🗑️")


def edit_mode_callback(section_key, index):
    st.session_state.edit_target = {'section': section_key, 'index': index}
    item = st.session_state[section_key][index]

    # Populate inputs
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


# --- 6. PDF Generator Class ---
class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', '', 9)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def section_title(self, label):
        self.ln(5)
        self.set_font('Times', 'B', 11)
        self.set_text_color(0)
        self.cell(0, 6, label.upper(), 0, 1, 'L')
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def add_item(self, title, date, subtitle, desc=None, is_bullet=False):
        self.set_font('Times', 'B', 10)
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

        if desc:
            self.set_font('Times', '', 10)
            if is_bullet:
                lines = desc.strip().split('\n')
                for line in lines:
                    if line.strip():
                        cl = line.strip().replace('-', '').replace('•', '').strip()
                        y = self.get_y()
                        self.set_xy(12, y)
                        self.cell(4, 4, chr(149), 0, 0)
                        self.set_xy(16, y)
                        self.multi_cell(0, 5, clean_text(cl))
            else:
                self.multi_cell(0, 5, clean_text(desc))
        self.ln(2)

    def add_simple(self, text):
        self.set_font('Times', '', 10)
        y = self.get_y()
        self.set_xy(12, y)
        self.cell(4, 4, chr(149), 0, 0)
        self.set_xy(16, y)
        self.multi_cell(0, 5, clean_text(text))


def generate_pdf_file(p, d):
    pdf = PDF('P', 'mm', 'A4')
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()

    # Header
    pdf.set_font('Times', 'B', 16)
    pdf.cell(0, 8, clean_text(p['name'].upper()), 0, 1, 'C')
    pdf.set_font('Times', '', 10)
    pdf.cell(0, 5, clean_text(f"{p['location']} | {p['phone']} | {p['email']}"), 0, 1, 'C')
    links = [l for l in [p['linkedin'], p['github']] if l]
    if links: pdf.cell(0, 5, " | ".join([clean_text(l) for l in links]), 0, 1, 'C')
    pdf.ln(5)

    if p['summary']:
        pdf.section_title('Professional Summary')
        pdf.set_font('Times', '', 10)
        pdf.multi_cell(0, 5, clean_text(p['summary']))

    if d['experience']:
        pdf.section_title('Professional Experience')
        for i in d['experience']: pdf.add_item(i['title'], i['date'], i['company'], i['desc'], True)

    if d['projects']:
        pdf.section_title('Technical Projects')
        for i in d['projects']: pdf.add_item(i['title'], i['date'], None, i['desc'], True)

    if d['education']:
        pdf.section_title('Education')
        for i in d['education']: pdf.add_item(i['degree'], i['date'], i['school'], None, False)

    if d['certs']:
        pdf.section_title('Certifications')
        for i in d['certs']: pdf.add_item(i['name'], i['date'], i['authority'], None, False)

    if d['skills']:
        pdf.section_title('Technical Skills')
        for i in d['skills']: pdf.add_simple(i['text'])

    if d['languages']:
        pdf.section_title('Languages')
        for i in d['languages']: pdf.add_simple(i['text'])

    return pdf


# --- 7. Validation & Dialogs ---
def get_validation_errors(name, email, data):
    errs = []
    if not name.strip(): errs.append("Full Name is required.")
    if not email.strip(): errs.append("Email Address is required.")

    # Check sections content
    if not any(data.values()):
        errs.append("Resume is empty! Add at least one Skill, Experience, or Education.")

    return errs


@st.dialog("⚠️ Missing Information")
def show_error_dialog(errors):
    st.markdown("<p style='font-size:14px; color:#E2E8F0'>Please fix the following issues to generate your resume:</p>",
                unsafe_allow_html=True)
    for err in errors:
        st.markdown(f"""
        <div style="background-color:rgba(255, 193, 7, 0.1); border-left:4px solid #FFC107; padding:10px; margin-bottom:8px; border-radius:4px;">
            <span style="color:#E2E8F0; font-size:14px;">{err}</span>
        </div>
        """, unsafe_allow_html=True)
    if st.button("Okay, I'll fix it", type="primary"):
        st.rerun()


@st.dialog("❌ System Error")
def show_crash_dialog(e):
    st.error(f"An unexpected error occurred: {e}")


# --- 8. UI Components ---
def render_header():
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.markdown("""
        <div style="width:50px; height:50px; border-radius:12px; background:linear-gradient(135deg, #6366F1, #8B5CF6);
        display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:20px;">AI</div>
        """, unsafe_allow_html=True)
    with col2:
        st.title("Resume Builder")
        st.caption("Professional, ATS-Optimized, and Error-Free.")


def render_section(key, title):
    with st.container():
        st.subheader(title)

        is_editing = (st.session_state.edit_target and st.session_state.edit_target['section'] == key)

        # Keys for inputs
        k1, k2, k3, k4 = f"t_{key}", f"c_{key}", f"d_{key}", f"desc_{key}"

        # Input Layout
        if key == 'experience':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text_input("Job Title", key=k1)
            c2.text_input("Company", key=k2)
            c3.text_input("Date", key=k3)
            st.text_area("Description (Bullet points)", key=k4, height=100)
        elif key == 'education':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text_input("Degree", key=k1)
            c2.text_input("Institution", key=k2)
            c3.text_input("Date", key=k3)
        elif key == 'projects':
            c1, c2 = st.columns([3, 1])
            c1.text_input("Project Name", key=k1)
            c2.text_input("Date", key=k3)
            st.text_area("Description (Bullet points)", key=k4, height=100)
        elif key == 'certs':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text_input("Certification Name", key=k1)
            c2.text_input("Authority", key=k2)
            c3.text_input("Date", key=k3)
        else:
            st.text_input("Item Name", key=k1)

        # Buttons
        b1, b2, _ = st.columns([1, 1, 6])

        if is_editing:
            idx = st.session_state.edit_target['index']
            b1.button("Save Changes", key=f"s_{key}", type="primary", on_click=save_changes_callback, args=(key, idx))
            b2.button("Cancel", key=f"x_{key}", kind="secondary", on_click=cancel_edit_callback, args=(key,))
        else:
            b1.button("Add Item", key=f"a_{key}", type="secondary", on_click=add_item_callback, args=(key,))

        # List Display
        if st.session_state[key]:
            st.markdown("---")
            for i, item in enumerate(st.session_state[key]):
                # Determine display text
                txt = item.get('title') or item.get('degree') or item.get('name') or item.get('text')
                date = item.get('date')

                # HTML styling for list item
                display_html = f"<div style='font-weight:500; color:#F1F5F9;'>{i + 1}. {txt}</div>"
                if date:
                    display_html += f"<div style='font-size:12px; color:#94A3B8; margin-top:-2px;'>{date}</div>"

                # Layout for row
                r1, r2, r3 = st.columns([0.85, 0.07, 0.08])
                r1.markdown(display_html, unsafe_allow_html=True)
                r2.button("✎", key=f"ed_{key}_{i}", on_click=edit_mode_callback, args=(key, i))
                r3.button("✖", key=f"del_{key}_{i}", on_click=delete_item_callback, args=(key, i))


# --- 9. Main Application Flow ---
render_header()

st.markdown("<br>", unsafe_allow_html=True)

# Identity Section
with st.container():
    st.subheader("👤 Identity")
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Full Name")
    email = c2.text_input("Email")
    phone = c3.text_input("Phone")

    c4, c5, c6 = st.columns(3)
    loc = c4.text_input("Location")
    link = c5.text_input("LinkedIn")
    git = c6.text_input("GitHub")

    summ = st.text_area("Professional Summary", height=80)

st.markdown("<br>", unsafe_allow_html=True)

# Content Sections
render_section('experience', 'Professional Experience')
render_section('projects', 'Technical Projects')
render_section('education', 'Education')
render_section('certs', 'Certifications')
render_section('skills', 'Technical Skills')
render_section('languages', 'Languages')

st.divider()

# Generate Button
if st.button("✨ GENERATE PDF RESUME", type="primary", use_container_width=True):
    # Collect data
    lists_data = {k: st.session_state[k] for k in KEYS}

    # Validation
    errors = get_validation_errors(name, email, lists_data)

    if errors:
        show_error_dialog(errors)
    else:
        # Generation
        try:
            profile_data = {
                'name': name, 'email': email, 'phone': phone,
                'location': loc, 'linkedin': link, 'github': git, 'summary': summ
            }

            pdf = generate_pdf_file(profile_data, lists_data)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                with open(tmp.name, "rb") as f:
                    st.toast("Resume generated successfully!", icon="🚀")
                    st.download_button(
                        label="📥 Download PDF",
                        data=f,
                        file_name=f"{name.replace(' ', '_')}_Resume.pdf",
                        mime="application/pdf"
                    )
            os.unlink(tmp.name)

        except Exception as e:
            show_crash_dialog(e)