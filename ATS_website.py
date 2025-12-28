import streamlit as st
from fpdf import FPDF
import tempfile
import os

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="ATS Master Resume",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. PROFESSIONAL STYLING (Outlier Theme) ---
st.markdown("""
<style>
    /* Background & Global Font */
    .stApp {
        background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Glassmorphism Cards */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 24px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    /* Input Fields styling */
    .stTextInput input, .stTextArea textarea {
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        color: #F8FAFC !important;
        border-radius: 6px;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.3);
    }

    /* Buttons */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stButton button[kind="secondary"] {
        background: transparent;
        border: 1px solid #64748B;
        color: #CBD5E1;
        border-radius: 6px;
    }

    /* Text Colors */
    h1, h2, h3 { color: #F1F5F9 !important; }
    p, label, span { color: #94A3B8 !important; }
    .stToast { background-color: #334155 !important; color: white !important; border: 1px solid #475569; }
</style>
""", unsafe_allow_html=True)

# --- 3. STATE MANAGEMENT ---
KEYS = ['experience', 'projects', 'education', 'certs', 'skills', 'languages']
for key in KEYS:
    if key not in st.session_state:
        st.session_state[key] = []
if 'edit_target' not in st.session_state:
    st.session_state.edit_target = None


# --- 4. CALLBACKS (Prevent Crashes) ---
def add_item_callback(section_key):
    k1, k2, k3, k4 = f"t_{section_key}", f"c_{section_key}", f"d_{section_key}", f"desc_{section_key}"
    v1 = st.session_state.get(k1, "").strip()
    v2 = st.session_state.get(k2, "").strip()
    v3 = st.session_state.get(k3, "").strip()
    v4 = st.session_state.get(k4, "").strip()

    new_item = {}
    valid = False

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
        for k in [k1, k2, k3, k4]:
            if k in st.session_state: st.session_state[k] = ""
        st.toast(f"Added to {section_key}", icon="✅")
    else:
        st.toast("Main field is required!", icon="⚠️")


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
    for k in [k1, k2, k3, k4]:
        if k in st.session_state: st.session_state[k] = ""
    st.toast("Updated successfully", icon="💾")


def delete_item_callback(section_key, index):
    st.session_state[section_key].pop(index)
    if st.session_state.edit_target and st.session_state.edit_target['section'] == section_key and \
            st.session_state.edit_target['index'] == index:
        st.session_state.edit_target = None
    st.toast("Deleted", icon="🗑️")


def edit_mode_callback(section_key, index):
    st.session_state.edit_target = {'section': section_key, 'index': index}
    item = st.session_state[section_key][index]
    # Populate fields
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


def cancel_edit_callback(section_key):
    st.session_state.edit_target = None
    for k in [f"t_{section_key}", f"c_{section_key}", f"d_{section_key}", f"desc_{section_key}"]:
        if k in st.session_state: st.session_state[k] = ""


# --- 5. ATS-OPTIMIZED PDF ENGINE ---
def clean_text(text):
    # Latin-1 ensures PDF compatibility. 'replace' handles unmapped chars gracefully.
    if text: return text.encode('latin-1', 'replace').decode('latin-1')
    return ""


class ATS_PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', '', 9)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def section_header(self, title):
        self.ln(5)
        self.set_font('Times', 'B', 11)
        self.set_text_color(0)  # Pure Black for ATS
        self.cell(0, 6, title.upper(), 0, 1, 'L')
        self.set_draw_color(0, 0, 0)  # Black line
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def add_entry(self, title, subtitle, date, description, is_bullet=False):
        # 1. Title & Date line
        self.set_font('Times', 'B', 10)

        # Smart spacing for date
        title_width = 140 if date else 190
        self.cell(title_width, 5, clean_text(title), 0, 0, 'L')

        if date:
            self.set_font('Times', '', 10)
            self.cell(0, 5, clean_text(date), 0, 1, 'R')
        else:
            self.ln(5)

        # 2. Subtitle (Company/School)
        if subtitle:
            self.set_font('Times', 'I', 10)  # Italic helps parser distinguish organization
            self.cell(0, 5, clean_text(subtitle), 0, 1, 'L')

        # 3. Description
        if description:
            self.set_font('Times', '', 10)
            if is_bullet:
                lines = description.strip().split('\n')
                for line in lines:
                    if line.strip():
                        # Remove existing bullets to avoid double bullets
                        cl = line.strip().replace('-', '').replace('•', '').strip()
                        current_y = self.get_y()
                        self.set_xy(12, current_y)
                        self.cell(4, 4, chr(149), 0, 0)  # Standard Bullet Char
                        self.set_xy(16, current_y)
                        self.multi_cell(0, 5, clean_text(cl))
            else:
                self.multi_cell(0, 5, clean_text(description))
        self.ln(2)

    def add_list_item(self, text):
        self.set_font('Times', '', 10)
        current_y = self.get_y()
        self.set_xy(12, current_y)
        self.cell(4, 4, chr(149), 0, 0)
        self.set_xy(16, current_y)
        self.multi_cell(0, 5, clean_text(text))


def generate_ats_pdf(p, d):
    pdf = ATS_PDF('P', 'mm', 'A4')
    pdf.set_auto_page_break(True, 15)
    pdf.set_title(f"{clean_text(p['name'])} - CV")
    pdf.set_author(clean_text(p['name']))
    pdf.add_page()

    # --- Header Block ---
    pdf.set_font('Times', 'B', 16)
    pdf.cell(0, 8, clean_text(p['name'].upper()), 0, 1, 'C')

    pdf.set_font('Times', '', 10)
    # Construct contact line carefully
    contact_parts = [p['location'], p['phone'], p['email']]
    contact_line = " | ".join([c for c in contact_parts if c])
    pdf.cell(0, 5, clean_text(contact_line), 0, 1, 'C')

    links = [l for l in [p['linkedin'], p['github']] if l]
    if links:
        pdf.cell(0, 5, " | ".join([clean_text(l) for l in links]), 0, 1, 'C')

    pdf.ln(5)

    # --- Sections (Order matters for ATS) ---
    if p['summary']:
        pdf.section_header('Professional Summary')
        pdf.set_font('Times', '', 10)
        pdf.multi_cell(0, 5, clean_text(p['summary']))

    if d['skills']:
        pdf.section_header('Technical Skills')
        # Listing skills as bullet points is safest for parsing
        for item in d['skills']: pdf.add_list_item(item['text'])

    if d['experience']:
        pdf.section_header('Professional Experience')
        for item in d['experience']:
            pdf.add_entry(item['title'], item['company'], item['date'], item['desc'], is_bullet=True)

    if d['projects']:
        pdf.section_header('Technical Projects')
        for item in d['projects']:
            pdf.add_entry(item['title'], None, item['date'], item['desc'], is_bullet=True)

    if d['education']:
        pdf.section_header('Education')
        for item in d['education']:
            pdf.add_entry(item['degree'], item['school'], item['date'], None, False)

    if d['certs']:
        pdf.section_header('Certifications')
        for item in d['certs']:
            pdf.add_entry(item['name'], item['authority'], item['date'], None, False)

    if d['languages']:
        pdf.section_header('Languages')
        for item in d['languages']: pdf.add_list_item(item['text'])

    return pdf


# --- 6. UI COMPONENTS ---
def render_header():
    c1, c2 = st.columns([0.1, 0.9])
    with c1:
        st.markdown("""
        <div style="width:50px;height:50px;background:linear-gradient(135deg, #6366F1, #8B5CF6);
        border-radius:12px;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:22px;">AI</div>
        """, unsafe_allow_html=True)
    with c2:
        st.title("ATS Master Resume")
        st.caption("Optimized for Applicant Tracking Systems (ATS) | Standard Layout | Clean Code")


def render_section_manager(key, title):
    with st.container():
        st.subheader(title)

        # Keys for input persistence
        k1, k2, k3, k4 = f"t_{key}", f"c_{key}", f"d_{key}", f"desc_{key}"

        # Determine mode
        is_editing = (st.session_state.edit_target and st.session_state.edit_target['section'] == key)

        # Input Layout
        if key == 'experience':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text_input("Job Title", key=k1)
            c2.text_input("Company", key=k2)
            c3.text_input("Date", key=k3)
            st.text_area("Description (Bullet Points)", key=k4, height=100)
        elif key == 'education':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text_input("Degree", key=k1)
            c2.text_input("Institution", key=k2)
            c3.text_input("Date", key=k3)
        elif key == 'projects':
            c1, c2 = st.columns([3, 1])
            c1.text_input("Project Name", key=k1)
            c2.text_input("Date", key=k3)
            st.text_area("Description (Bullet Points)", key=k4, height=100)
        elif key == 'certs':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text_input("Certification Name", key=k1)
            c2.text_input("Authority", key=k2)
            c3.text_input("Date", key=k3)
        else:
            st.text_input("Item Name / Skill", key=k1)

        # Actions
        b1, b2, _ = st.columns([1, 1, 6])
        if is_editing:
            idx = st.session_state.edit_target['index']
            b1.button("Save Changes", key=f"save_{key}", type="primary", on_click=save_changes_callback,
                      args=(key, idx))
            b2.button("Cancel", key=f"can_{key}", kind="secondary", on_click=cancel_edit_callback, args=(key,))
        else:
            b1.button("Add Item", key=f"add_{key}", type="secondary", on_click=add_item_callback, args=(key,))

        # Display List
        if st.session_state[key]:
            st.markdown("---")
            for i, item in enumerate(st.session_state[key]):
                # Formatting display text
                main_txt = item.get('title') or item.get('degree') or item.get('name') or item.get('text')
                sub_txt = item.get('company') or item.get('school') or item.get('authority')
                date_txt = item.get('date')

                # HTML Item View
                html = f"<div style='color:#F8FAFC; font-weight:500;'>{i + 1}. {main_txt}</div>"
                if sub_txt: html += f"<div style='color:#94A3B8; font-size:13px; margin-left:18px;'>{sub_txt}</div>"
                if date_txt: html += f"<div style='color:#64748B; font-size:12px; margin-left:18px;'>{date_txt}</div>"

                r1, r2, r3 = st.columns([0.85, 0.07, 0.08])
                r1.markdown(html, unsafe_allow_html=True)
                r2.button("✎", key=f"e_{key}_{i}", on_click=edit_mode_callback, args=(key, i))
                r3.button("✖", key=f"d_{key}_{i}", on_click=delete_item_callback, args=(key, i))


# --- 7. ERROR DIALOGS ---
@st.dialog("⚠️ Resume Incomplete")
def show_validation_error(errors):
    st.markdown("Please fix the following to ensure ATS compatibility:")
    for e in errors:
        st.markdown(
            f"<div style='background:rgba(255,193,7,0.1);padding:8px;border-left:4px solid #FFC107;margin-bottom:5px;font-size:14px;'>{e}</div>",
            unsafe_allow_html=True)
    if st.button("Okay"): st.rerun()


@st.dialog("❌ Generation Error")
def show_system_error(e):
    st.error(f"System Error: {e}")


# --- 8. MAIN APP FLOW ---
render_header()
st.markdown("<br>", unsafe_allow_html=True)

with st.container():
    st.subheader("👤 Contact Information")
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Full Name")
    email = c2.text_input("Email")
    phone = c3.text_input("Phone")
    c4, c5, c6 = st.columns(3)
    loc = c4.text_input("Location")
    link = c5.text_input("LinkedIn")
    git = c6.text_input("GitHub")
    summ = st.text_area("Professional Summary", height=100)

st.markdown("<br>", unsafe_allow_html=True)

render_section_manager('experience', 'Professional Experience')
render_section_manager('projects', 'Technical Projects')
render_section_manager('education', 'Education')
render_section_manager('certs', 'Certifications')
render_section_manager('skills', 'Technical Skills')
render_section_manager('languages', 'Languages')

st.divider()

if st.button("🚀 GENERATE ATS-COMPLIANT RESUME", type="primary", use_container_width=True):
    # Validation
    errors = []
    if not name.strip(): errors.append("Full Name is required.")
    if not email.strip(): errors.append("Email is required.")
    if not st.session_state.experience and not st.session_state.education:
        errors.append("Add at least one Experience or Education entry.")

    if errors:
        show_validation_error(errors)
    else:
        try:
            p_data = {'name': name, 'email': email, 'phone': phone, 'location': loc, 'linkedin': link, 'github': git,
                      'summary': summ}
            l_data = {k: st.session_state[k] for k in KEYS}

            pdf = generate_ats_pdf(p_data, l_data)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                with open(tmp.name, "rb") as f:
                    st.toast("Resume Generated! Ready for Download.", icon="🎉")
                    st.download_button("📥 Download ATS Resume", f, f"{name.replace(' ', '_')}_CV.pdf",
                                       "application/pdf")
            os.unlink(tmp.name)
        except Exception as e:
            show_system_error(e)