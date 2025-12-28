import streamlit as st
from fpdf import FPDF
import tempfile
import os

# --- Page Config ---
st.set_page_config(page_title="Ultimate Resume Builder", page_icon="💼", layout="centered")

# --- Session State Initialization (Database) ---
# Initialize lists if they don't exist
for key in ['experience', 'projects', 'education', 'certs', 'skills', 'languages']:
    if key not in st.session_state:
        st.session_state[key] = []

# Initialize Edit State (To track what we are editing)
if 'edit_target' not in st.session_state:
    st.session_state.edit_target = None  # Stores: {'section': 'experience', 'index': 0}


# --- PDF Generation Logic ---
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
        self.ln(5)
        self.set_font('Times', 'B', 12)
        self.set_text_color(0)
        self.cell(0, 6, label.upper(), 0, 1, 'L')
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def add_item(self, title, subtitle=None, is_bullet=False):
        # Title
        self.set_font('Times', 'B', 11)
        self.multi_cell(0, 5, clean_text(title))

        # Subtitle / Description
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
    pdf.set_font('Times', 'B', 16)
    pdf.cell(0, 8, clean_text(personal['name'].upper()), 0, 1, 'C')
    pdf.set_font('Times', '', 11)
    pdf.cell(0, 5, clean_text(f"{personal['location']} | {personal['phone']} | {personal['email']}"), 0, 1, 'C')
    links = [l for l in [personal['linkedin'], personal['github']] if l]
    if links: pdf.cell(0, 5, " | ".join([clean_text(l) for l in links]), 0, 1, 'C')
    pdf.ln(5)

    # Summary
    if personal['summary']:
        pdf.section_title('Professional Summary')
        pdf.set_font('Times', '', 11)
        pdf.multi_cell(0, 5, clean_text(personal['summary']))

    # Sections
    sections_map = [
        ('Technical Skills', 'skills', False),  # False means not bullet list inside
        ('Professional Experience', 'experience', True),
        ('Technical Projects', 'projects', True),
        ('Education', 'education', False),
        ('Certifications', 'certs', False),
        ('Languages', 'languages', False)
    ]

    for title, key, is_complex in sections_map:
        if data[key]:
            pdf.section_title(title)
            for item in data[key]:
                # Handle different structures
                if key in ['experience', 'projects']:
                    pdf.add_item(item['title'], item['desc'], is_bullet=True)
                elif key == 'education':
                    pdf.add_item(item['degree'], item['details'])
                elif key == 'certs':
                    pdf.add_item(item['name'], item['auth'])
                elif key in ['skills', 'languages']:
                    # Simple list item
                    pdf.set_font('Times', '', 11)
                    y = pdf.get_y()
                    pdf.set_xy(12, y)
                    pdf.cell(5, 5, chr(149), 0, 0)
                    pdf.set_xy(17, y)
                    pdf.multi_cell(0, 5, clean_text(item['text']))

    return pdf


# --- HELPER: Section Manager (The Magic Function) ---
def section_manager(section_key, title_label, desc_label=None):
    st.divider()
    st.subheader(section_key.replace('_', ' ').title())

    # Check if we are editing THIS section
    is_editing = (st.session_state.edit_target and
                  st.session_state.edit_target['section'] == section_key)
    edit_idx = st.session_state.edit_target['index'] if is_editing else None

    # Get default values if editing
    default_title = ""
    default_desc = ""

    if is_editing:
        item = st.session_state[section_key][edit_idx]
        # Mapping keys based on section type
        if section_key in ['experience', 'projects']:
            default_title = item['title']
            default_desc = item['desc']
        elif section_key == 'education':
            default_title = item['degree']
            default_desc = item['details']
        elif section_key == 'certs':
            default_title = item['name']
            default_desc = item['auth']
        elif section_key in ['skills', 'languages']:
            default_title = item['text']

    # Inputs
    with st.container(border=True):
        c1, c2 = st.columns([1, 2] if desc_label else [1, 0.01])

        # Title Input
        new_title = c1.text_input(title_label, value=default_title, key=f"in_{section_key}_title")

        # Description Input (Optional)
        new_desc = ""
        if desc_label:
            new_desc = c2.text_area(desc_label, value=default_desc, height=100, key=f"in_{section_key}_desc")

        # Action Button (Add or Update)
        btn_col, _ = st.columns([1, 4])
        if is_editing:
            if btn_col.button(f"🔄 Update {section_key[:-1].title()}", key=f"btn_upd_{section_key}"):
                # Logic to Save Update
                new_data = {}
                if section_key in ['experience', 'projects']:
                    new_data = {'title': new_title, 'desc': new_desc}
                elif section_key == 'education':
                    new_data = {'degree': new_title, 'details': new_desc}
                elif section_key == 'certs':
                    new_data = {'name': new_title, 'auth': new_desc}
                elif section_key in ['skills', 'languages']:
                    new_data = {'text': new_title}

                st.session_state[section_key][edit_idx] = new_data
                st.session_state.edit_target = None  # Exit edit mode
                st.rerun()

            if btn_col.button("Cancel Edit", key=f"cancel_{section_key}"):
                st.session_state.edit_target = None
                st.rerun()
        else:
            if btn_col.button(f"➕ Add {section_key[:-1].title()}", key=f"btn_add_{section_key}"):
                if new_title:
                    new_data = {}
                    if section_key in ['experience', 'projects']:
                        new_data = {'title': new_title, 'desc': new_desc}
                    elif section_key == 'education':
                        new_data = {'degree': new_title, 'details': new_desc}
                    elif section_key == 'certs':
                        new_data = {'name': new_title, 'auth': new_desc}
                    elif section_key in ['skills', 'languages']:
                        new_data = {'text': new_title}

                    st.session_state[section_key].append(new_data)
                    st.rerun()
                else:
                    st.error("Title/Name is required!")

    # List Display with Edit/Delete
    if st.session_state[section_key]:
        for i, item in enumerate(st.session_state[section_key]):
            # Determine display text
            if section_key in ['experience', 'projects']:
                display_txt = item['title']
            elif section_key == 'education':
                display_txt = item['degree']
            elif section_key == 'certs':
                display_txt = item['name']
            else:
                display_txt = item['text']

            cols = st.columns([0.8, 0.1, 0.1])
            cols[0].markdown(f"**{i + 1}. {display_txt}**")

            # Edit Button
            if cols[1].button("✏️", key=f"edit_{section_key}_{i}"):
                st.session_state.edit_target = {'section': section_key, 'index': i}
                st.rerun()

            # Delete Button
            if cols[2].button("❌", key=f"del_{section_key}_{i}"):
                st.session_state[section_key].pop(i)
                # If we deleted the item being edited, exit edit mode
                if is_editing and edit_idx == i:
                    st.session_state.edit_target = None
                st.rerun()


# --- MAIN UI ---
st.title("🚀 Ultimate Resume Generator")

with st.expander("📝 Personal Information", expanded=True):
    c1, c2 = st.columns(2)
    name = c1.text_input("Full Name", "Saif Eldien Yehia")
    email = c1.text_input("Email")
    linkedin = c1.text_input("LinkedIn")
    location = c2.text_input("Location")
    phone = c2.text_input("Phone")
    github = c2.text_input("GitHub")
    summary = st.text_area("Professional Summary", height=80)

# --- Calling the Manager for each section ---

# 1. Skills
section_manager('skills', 'Skill Name (e.g. Python)', None)

# 2. Experience
section_manager('experience', 'Job Title | Company | Date', 'Description (Bullets)')

# 3. Projects
section_manager('projects', 'Project Name', 'Description (Bullets)')

# 4. Education
section_manager('education', 'Degree Name', 'Institution | Date')

# 5. Certifications
section_manager('certs', 'Certification Name', 'Authority / Date')

# 6. Languages
section_manager('languages', 'Language (e.g. Arabic: Native)', None)

# --- Generate Button ---
st.divider()
if st.button("✅ GENERATE PDF RESUME", type="primary", use_container_width=True):
    if not name:
        st.error("Name is required!")
    else:
        personal_data = {
            'name': name, 'email': email, 'phone': phone, 'location': location,
            'linkedin': linkedin, 'github': github, 'summary': summary
        }
        list_data = {
            'skills': st.session_state.skills,
            'experience': st.session_state.experience,
            'projects': st.session_state.projects,
            'education': st.session_state.education,
            'certs': st.session_state.certs,
            'languages': st.session_state.languages
        }

        try:
            pdf = generate_pdf(personal_data, list_data)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                with open(tmp.name, "rb") as f:
                    st.success("Resume Ready!")
                    st.download_button("📥 Download PDF", f, f"{name}_Resume.pdf", "application/pdf")
            os.unlink(tmp.name)
        except Exception as e:
            st.error(f"Error: {e}")
