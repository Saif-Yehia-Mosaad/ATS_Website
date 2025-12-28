import streamlit as st
from fpdf import FPDF
import tempfile
import os

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="Professional Resume Builder",
    page_icon="👔",
    layout="centered"
)

# --- تهيئة الذاكرة لحفظ القوائم (Experience & Projects) ---
if 'experience_list' not in st.session_state:
    st.session_state.experience_list = []
if 'projects_list' not in st.session_state:
    st.session_state.projects_list = []


# --- دالة تنظيف النصوص ---
def clean_text(text):
    if text:
        # تحويل النص إلى صيغة لاتينية لتجنب الأخطاء
        return text.encode('latin-1', 'replace').decode('latin-1')
    return ""


# --- كلاس بناء الـ PDF ---
class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', '', 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def section_title(self, label):
        self.ln(5)
        self.set_font('Times', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, label.upper(), 0, 1, 'L')
        self.line(10, self.get_y(), 200, self.get_y())  # خط فاصل
        self.ln(2)

    # دالة رسم عنصر مركب (عنوان عريض + تفاصيل عادية)
    def add_complex_item(self, title, description):
        # 1. العنوان (Headline) بخط Bold
        self.set_font('Times', 'B', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, clean_text(title))

        # 2. التفاصيل (Description) بخط عادي مع نقاط
        if description:
            self.set_font('Times', '', 11)
            lines = description.strip().split('\n')
            for line in lines:
                if line.strip():
                    # تنظيف السطر من أي رموز قديمة
                    clean_line = line.strip().replace('-', '').replace('•', '').strip()

                    # رسم النقطة
                    current_y = self.get_y()
                    self.set_xy(12, current_y)
                    self.cell(5, 5, chr(149), 0, 0)  # رمز •

                    # رسم النص
                    self.set_xy(17, current_y)
                    self.multi_cell(0, 5, clean_text(clean_line))
            self.ln(2)  # مسافة بعد كل عنصر

    def add_simple_text(self, text):
        self.set_font('Times', '', 11)
        self.multi_cell(0, 5, clean_text(text))
        self.ln(1)


def generate_pdf(data):
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # --- Header ---
    pdf.set_font('Times', 'B', 16)
    pdf.cell(0, 8, clean_text(data['name'].upper()), 0, 1, 'C')

    pdf.set_font('Times', '', 11)
    contact_info = f"{clean_text(data['location'])} | {clean_text(data['phone'])} | {clean_text(data['email'])}"
    pdf.cell(0, 5, contact_info, 0, 1, 'C')

    links = []
    if data['linkedin']: links.append(clean_text(data['linkedin']))
    if data['github']: links.append(clean_text(data['github']))
    if links:
        pdf.cell(0, 5, " | ".join(links), 0, 1, 'C')

    pdf.ln(5)

    # --- Body Sections ---

    # Summary
    if data['summary']:
        pdf.section_title('Professional Summary')
        pdf.add_simple_text(data['summary'])

    # Skills (simple list text)
    if data['skills']:
        pdf.section_title('Technical Skills')
        # معالجة المهارات كنقاط بسيطة
        lines = data['skills'].split('\n')
        for line in lines:
            if line.strip():
                pdf.set_font('Times', '', 11)
                pdf.set_xy(12, pdf.get_y())
                pdf.cell(5, 5, chr(149), 0, 0)
                pdf.set_xy(17, pdf.get_y())
                pdf.multi_cell(0, 5, clean_text(line.strip()))

    # Experience (Loop through list)
    if st.session_state.experience_list:
        pdf.section_title('Professional Experience')
        for item in st.session_state.experience_list:
            pdf.add_complex_item(item['title'], item['desc'])

    # Projects (Loop through list)
    if st.session_state.projects_list:
        pdf.section_title('Technical Projects')
        for item in st.session_state.projects_list:
            pdf.add_complex_item(item['title'], item['desc'])

    # Education
    if data['education']:
        pdf.section_title('Education')
        pdf.add_simple_text(data['education'])

    # Certifications
    if data['certs']:
        pdf.section_title('Certifications')
        pdf.add_simple_text(data['certs'])

    # Languages
    if data['languages']:
        pdf.section_title('Languages')
        pdf.add_simple_text(data['languages'])

    return pdf


# --- واجهة المستخدم (Streamlit UI) ---
st.title("📄 Professional Resume Builder")
st.markdown("Add your details below. For **Experience** and **Projects**, add items one by one.")

with st.form("main_form"):
    st.subheader("1. Personal Info")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", placeholder="Saif Eldien Yehia")
        email = st.text_input("Email")
        linkedin = st.text_input("LinkedIn URL")
    with col2:
        location = st.text_input("Location")
        phone = st.text_input("Phone Number")
        github = st.text_input("GitHub URL")

    st.subheader("2. Summary")
    summary = st.text_area("Professional Summary", height=80)

    st.subheader("3. Technical Skills")
    skills = st.text_area("List your skills (One per line)", height=100)

    st.subheader("4. Education & Certs")
    education = st.text_area("Education Details")
    certs = st.text_area("Certifications")
    languages = st.text_area("Languages")

    # زر الحفظ المبدئي (للبيانات الأساسية فقط)
    # لا نضع زر Experience هنا لأننا سنستخدم واجهة ديناميكية خارج الفورم
    submitted_main = st.form_submit_button("Save Basic Info & Continue")

# --- المنطقة الديناميكية (Experience & Projects) ---
st.divider()

# قسم الخبرات (Experience Section)
st.subheader("5. Professional Experience")
col_exp1, col_exp2 = st.columns([1, 2])
with col_exp1:
    exp_title = st.text_input("Job Title | Company | Date", key="exp_title_input",
                              placeholder="e.g. Backend Dev | Company X | 2024")
with col_exp2:
    exp_desc = st.text_area("Description (Bullet points)", key="exp_desc_input",
                            placeholder="- Developed API...\n- Fixed bugs...")

if st.button("➕ Add Experience Item"):
    if exp_title:
        st.session_state.experience_list.append({'title': exp_title, 'desc': exp_desc})
        st.success(f"Added: {exp_title}")
    else:
        st.error("Headline is required!")

# عرض ما تم إضافته
if st.session_state.experience_list:
    st.write("Current Experience List:")
    for idx, item in enumerate(st.session_state.experience_list):
        st.text(f"{idx + 1}. {item['title']}")
    if st.button("Clear Experience List"):
        st.session_state.experience_list = []

st.divider()

# قسم المشاريع (Projects Section)
st.subheader("6. Technical Projects")
col_proj1, col_proj2 = st.columns([1, 2])
with col_proj1:
    proj_title = st.text_input("Project Name", key="proj_title_input", placeholder="e.g. E-Commerce API")
with col_proj2:
    proj_desc = st.text_area("Description (Bullet points)", key="proj_desc_input",
                             placeholder="- Built using .NET 8...\n- Implemented JWT...")

if st.button("➕ Add Project"):
    if proj_title:
        st.session_state.projects_list.append({'title': proj_title, 'desc': proj_desc})
        st.success(f"Added: {proj_title}")
    else:
        st.error("Project Name is required!")

# عرض المشاريع المضافة
if st.session_state.projects_list:
    st.write("Current Projects List:")
    for idx, item in enumerate(st.session_state.projects_list):
        st.text(f"{idx + 1}. {item['title']}")
    if st.button("Clear Projects List"):
        st.session_state.projects_list = []

st.divider()

# --- زر التوليد النهائي ---
generate_btn = st.button("✅ GENERATE PDF RESUME", type="primary")

if generate_btn:
    if not name:
        st.error("Please go back and enter your Name in the top form.")
    else:
        # تجميع البيانات
        data = {
            'name': name, 'email': email, 'phone': phone, 'location': location,
            'linkedin': linkedin, 'github': github, 'summary': summary,
            'skills': skills, 'education': education, 'certs': certs, 'languages': languages
        }

        try:
            pdf = generate_pdf(data)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                pdf.output(tmp_file.name)
                with open(tmp_file.name, "rb") as f:
                    pdf_bytes = f.read()

                st.success("Resume Generated Successfully!")
                st.download_button(
                    label="📥 Download Final PDF",
                    data=pdf_bytes,
                    file_name=f"{name.replace(' ', '_')}_Resume.pdf",
                    mime="application/pdf"
                )
            os.unlink(tmp_file.name)
        except Exception as e:
            st.error(f"Error: {e}")