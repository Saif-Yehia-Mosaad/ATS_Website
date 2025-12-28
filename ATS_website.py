import streamlit as st
from fpdf import FPDF
import tempfile
import os

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="ATS Resume Generator",
    page_icon="📄",
    layout="centered"
)


# --- 1. محرك بناء الـ PDF ---
class ATS_PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', '', 10)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def section_title(self, label):
        self.ln(6)
        self.set_font('Times', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, label.upper(), 0, 1, 'L')
        self.ln(1)

    def add_bullet(self, text):
        self.set_font('Times', '', 11)
        self.cell(5)
        self.cell(3, 5, '-', 0, 0)
        self.multi_cell(0, 5, text)
        self.ln(1)


def generate_pdf(data):
    pdf = ATS_PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font('Times', 'B', 16)
    pdf.cell(0, 8, data['name'], 0, 1, 'C')

    pdf.set_font('Times', '', 11)
    pdf.ln(2)
    pdf.cell(0, 5, f"{data['location']} | {data['phone']} | {data['email']}", 0, 1, 'C')

    links = []
    if data['linkedin']: links.append(data['linkedin'])
    if data['github']: links.append(data['github'])
    if links:
        pdf.ln(2)
        pdf.cell(0, 5, "  |  ".join(links), 0, 1, 'C')

    pdf.ln(4)

    # Helper function
    def add_section(title, content, is_bullet=False):
        if content.strip():
            pdf.section_title(title)
            lines = content.strip().split('\n')
            for line in lines:
                if line.strip():
                    if is_bullet:
                        pdf.add_bullet(line.strip())
                    else:
                        pdf.multi_cell(0, 5, line.strip())
                        pdf.ln(1)

    add_section('Professional Summary', data['summary'])
    add_section('Technical Skills', data['skills'], is_bullet=True)
    add_section('Professional Experience', data['experience'], is_bullet=True)
    add_section('Technical Projects', data['projects'], is_bullet=True)
    add_section('Education', data['education'], is_bullet=True)
    add_section('Certifications', data['certs'], is_bullet=True)
    add_section('Languages', data['languages'], is_bullet=True)

    return pdf


# --- 2. واجهة الموقع ---
st.title("📄 ATS-Optimized Resume Generator")
st.markdown("Create a professional, **ATS-friendly** resume in seconds. Free & Instant.")

with st.form("cv_form"):
    st.subheader("Personal Info")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", placeholder="Saif Eldien Yehia")
        email = st.text_input("Email", placeholder="saif@example.com")
        linkedin = st.text_input("LinkedIn URL")
    with col2:
        location = st.text_input("Location", placeholder="Port Said, Egypt")
        phone = st.text_input("Phone Number")
        github = st.text_input("GitHub URL")

    st.subheader("Professional Summary")
    summary = st.text_area("Summary", height=100, help="Brief overview of your career.")

    st.subheader("Details (Put each item on a new line)")
    skills = st.text_area("Technical Skills", height=150, placeholder="Python\nC#\nSQL Server")
    experience = st.text_area("Experience", height=150,
                              placeholder="Job Title | Company | Date\n- Achieved X\n- Built Y")
    projects = st.text_area("Projects", height=150, placeholder="Project Name: Description")
    education = st.text_area("Education", height=100)
    certs = st.text_area("Certifications", height=100)
    languages = st.text_area("Languages", height=80)

    submitted = st.form_submit_button("Generate PDF Resume 🚀")

if submitted:
    if not name or not email:
        st.error("Please fill in Name and Email!")
    else:
        data = {
            'name': name, 'email': email, 'phone': phone, 'location': location,
            'linkedin': linkedin, 'github': github, 'summary': summary,
            'skills': skills, 'experience': experience, 'projects': projects,
            'education': education, 'certs': certs, 'languages': languages
        }


        # إنشاء ملف مؤقت للتحميل
        pdf = generate_pdf(data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf.output(tmp_file.name)

            with open(tmp_file.name, "rb") as f:
                pdf_bytes = f.read()

            st.success("✅ Resume Generated Successfully!")
            st.download_button(
                label="📥 Download PDF",
                data=pdf_bytes,
                file_name=f"{name.replace(' ', '_')}_CV.pdf",
                mime="application/pdf"
            )
        os.unlink(tmp_file.name)