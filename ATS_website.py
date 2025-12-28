import streamlit as st
from fpdf import FPDF
import tempfile
import os

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="ATS Master Resume",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. PROFESSIONAL STYLING ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 24px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        color: #F8FAFC !important;
        border-radius: 6px;
    }
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        border-radius: 6px;
    }
    .stButton button[kind="secondary"] {
        background: transparent;
        border: 1px solid #64748B;
        color: #CBD5E1;
        border-radius: 6px;
    }
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


# --- 4. LOGIC & TEXT CLEANING ---
def clean_text(text):
    """
    Cleans text for ATS parsing:
    1. Replaces fancy hyphens with standard ones (Fixes 'enterprisegrade' issue).
    2. Encodes to Latin-1 for PDF compatibility.
    """
    if text:
        # Replace non-standard characters that confuse ATS
        text = text.replace('–', '-').replace('—', '-').replace('’', "'").replace('“', '"').replace('”', '"')
        return text.encode('latin-1', 'replace').decode('latin-1')
    return ""


# --- 5. CALLBACKS ---
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
    st.toast("Changes saved", icon="💾")


def delete_item_callback(section_key, index):
    st.session_state[section_key].pop(index)
    if st.session_state.edit_target and st.session_state.edit_target['section'] == section_key and \
            st.session_state.edit_target['index'] == index:
        st.session_state.edit_target = None
    st.toast("Item deleted", icon="🗑️")


def edit_mode_callback(section_key, index):
    st.session_state.edit_target = {'section': section_key, 'index': index}
    item = st.session_state[section_key][index]
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


# --- 6. ATS PDF ENGINE ---
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
        self.set_text_color(0)
        self.cell(0, 6, title.upper(), 0, 1, 'L')
        self.set_draw_color(0, 0, 0)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def add_entry(self, title, subtitle, date, description, is_bullet=False):
        self.set_font('Times', 'B', 10)
        title_width = 140 if date else 190
        self.cell(title_width, 5, clean_text(title), 0, 0, 'L')

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
            if is_bullet:
                lines = description.strip().split('\n')
                for line in lines:
                    if line.strip():
                        cl = line.strip().replace('-', '').replace('•', '').strip()
                        y = self.get_y()
                        self.set_xy(12, y)
                        self.cell(4, 4, chr(149), 0, 0)
                        self.set_xy(16, y)
                        self.multi_cell(0, 5, clean_text(cl))
            else:
                self.multi_cell(0, 5, clean_text(description))
        self.ln(2)

    def add_list_item(self, text):
        self.set_font('Times', '', 10)
        y = self.get_y()
        self.set_xy(12, y)
        self.cell(4, 4, chr(149), 0, 0)
        self.set_xy(16, y)
        self.multi_cell(0, 5, clean_text(text))


def generate_ats_pdf(p, d):
    pdf = ATS_PDF('P', 'mm', 'A4')
    pdf.set_auto_page_break(True, 15)
    pdf.set_title(f"{clean_text(p['name'])} Resume")
    pdf.set_author(clean_text(p['name']))
    pdf.add_page()

    # Header
    pdf.set_font('Times', 'B', 16)
    pdf.cell(0, 8, clean_text(p['name'].upper()), 0, 1, 'C')

    pdf.set_font('Times', '', 10)
    parts = [p['location'], p['phone'], p['email']]
    line1 = " | ".join([x for x in parts if x])
    pdf.cell(0, 5, clean_text(line1), 0, 1, 'C')

    links = [l for l in [p['linkedin'], p['github']] if l]
    if links:
        pdf.cell(0, 5, " | ".join([clean_text(l) for l in links]), 0, 1, 'C')
    pdf.ln(5)

    if p['summary']:
        pdf.section_header('Professional Summary')
        pdf.set_font('Times', '', 10)
        pdf.multi_cell(0, 5, clean_text(p['summary']))

    if d['skills']:
        pdf.section_header('Technical Skills')
        for i in d['skills']: pdf.add_list_item(i['text'])

    if d['experience']:
        pdf.section_header('Professional Experience')
        for i in d['experience']: pdf.add_entry(i['title'], i['company'], i['date'], i['desc'], True)

    if d['projects']:
        pdf.section_header('Technical Projects')
        for i in d['projects']: pdf.add_entry(i['title'], None, i['date'], i['desc'], True)

    if d['education']:
        pdf.section_header('Education')
        for i in d['education']: pdf.add_entry(i['degree'], i['school'], i['date'], None, False)

    if d['certs']:
        pdf.section_header('Certifications')
        for i in d['certs']: pdf.add_entry(i['name'], i['authority'], i['date'], None, False)

    if d['languages']:
        pdf.section_header('Languages')
        for i in d['languages']: pdf.add_list_item(i['text'])

    return pdf


# --- 7. UI RENDERER ---
def render_header():
    c1, c2 = st.columns([0.1, 0.9])
    with c1:
        st.markdown("""
        <div style="width:50px;height:50px;background:linear-gradient(135deg, #6366F1, #8B5CF6);
        border-radius:12px;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:20px;">ATS</div>
        """, unsafe_allow_html=True)
    with c2:
        st.title("ATS Master Resume")
        st.caption("Score 95%+ with this Optimized Builder")


def render_section_manager(key, title, placeholder1=""):
    with st.container():
        st.subheader(title)
        is_editing = (st.session_state.edit_target and st.session_state.edit_target['section'] == key)
        k1, k2, k3, k4 = f"t_{key}", f"c_{key}", f"d_{key}", f"desc_{key}"

        if key == 'experience':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text_input("Job Title", key=k1, placeholder="e.g. .NET Developer")
            c2.text_input("Company", key=k2, placeholder="e.g. Microsoft")
            c3.text_input("Date", key=k3, placeholder="Jan 2023 - Present")
            st.text_area("Description", key=k4, height=100, placeholder="• Developed scalable APIs...")
        elif key == 'education':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text_input("Degree", key=k1, placeholder="B.Sc. Computer Science")
            c2.text_input("Institution", key=k2)
            c3.text_input("Date", key=k3)
        elif key == 'projects':
            c1, c2 = st.columns([3, 1])
            c1.text_input("Project Name", key=k1, placeholder="e.g. E-Commerce API")
            c2.text_input("Date", key=k3)
            st.text_area("Description", key=k4, height=100, placeholder="• Built using ASP.NET Core...")
        elif key == 'certs':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text_input("Certification Name", key=k1, placeholder="e.g. AWS Certified")
            c2.text_input("Authority", key=k2)
            c3.text_input("Date", key=k3)
        else:
            st.text_input("Skill / Language", key=k1, placeholder=placeholder1)

        b1, b2, _ = st.columns([1, 1, 6])
        if is_editing:
            idx = st.session_state.edit_target['index']
            b1.button("Save", key=f"s_{key}", type="primary", on_click=save_changes_callback, args=(key, idx))
            b2.button("Cancel", key=f"x_{key}", kind="secondary", on_click=cancel_edit_callback, args=(key,))
        else:
            b1.button("Add", key=f"a_{key}", type="secondary", on_click=add_item_callback, args=(key,))

        if st.session_state[key]:
            st.markdown("---")
            for i, item in enumerate(st.session_state[key]):
                txt = item.get('title') or item.get('degree') or item.get('name') or item.get('text')
                sub = item.get('company') or item.get('school') or item.get('authority')
                date = item.get('date')

                html = f"<div style='color:#F8FAFC; font-weight:500;'>{i + 1}. {txt}</div>"
                if sub: html += f"<div style='color:#94A3B8; font-size:13px; margin-left:18px;'>{sub}</div>"
                if date: html += f"<div style='color:#64748B; font-size:12px; margin-left:18px;'>{date}</div>"

                r1, r2, r3 = st.columns([0.85, 0.07, 0.08])
                r1.markdown(html, unsafe_allow_html=True)
                r2.button("✎", key=f"e_{key}_{i}", on_click=edit_mode_callback, args=(key, i))
                r3.button("✖", key=f"d_{key}_{i}", on_click=delete_item_callback, args=(key, i))


# --- 8. MAIN APP ---
render_header()
st.markdown("<br>", unsafe_allow_html=True)

with st.container():
    st.subheader("👤 Contact Info")
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Full Name", placeholder="Saif Eldien Yehia")
    email = c2.text_input("Email", placeholder="saif@example.com")
    phone = c3.text_input("Phone", placeholder="+20 123 456 7890")
    c4, c5, c6 = st.columns(3)
    loc = c4.text_input("Location", placeholder="Port Said, Egypt (Correct Spelling)")
    link = c5.text_input("LinkedIn")
    git = c6.text_input("GitHub")
    summ = st.text_area("Summary", height=100, placeholder="Results-oriented .NET Developer...")

st.markdown("<br>", unsafe_allow_html=True)

render_section_manager('experience', 'Professional Experience')
render_section_manager('projects', 'Technical Projects')
render_section_manager('education', 'Education')
render_section_manager('skills', 'Technical Skills', placeholder1="e.g. CI/CD, Azure, Docker (Add these!)")
render_section_manager('certs', 'Certifications')
render_section_manager('languages', 'Languages')

st.divider()

if st.button("🚀 GENERATE RESUME", type="primary", use_container_width=True):
    if not name or not email:
        st.toast("Full Name and Email are required!", icon="⚠️")
    else:
        try:
            p_data = {'name': name, 'email': email, 'phone': phone, 'location': loc, 'linkedin': link, 'github': git,
                      'summary': summ}
            l_data = {k: st.session_state[k] for k in KEYS}

            pdf = generate_ats_pdf(p_data, l_data)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                with open(tmp.name, "rb") as f:
                    st.toast("Success! Resume Generated.", icon="🎉")
                    st.download_button("📥 Download PDF", f, f"{name.replace(' ', '_')}_CV.pdf", "application/pdf")
            os.unlink(tmp.name)
        except Exception as e:
            st.error(f"Error: {e}")