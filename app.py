import json
import re
import docx
import PyPDF2
import streamlit as st

st.set_page_config(
    page_title="GradMatch AI",
    page_icon="🎓",
    layout="wide"
)

# Load skills database
def load_skills_database():
    with open("skills_database.json", "r") as file:
        return json.load(file)

skills_db = load_skills_database()

# Theme
theme = st.sidebar.radio("Choose theme", ["Light", "Dark"])

if theme == "Light":
    bg = "#f4f7fb"
    card = "#ffffff"
    text = "#111827"
    input_bg = "#ffffff"
    border = "#d1d5db"
    hero = "linear-gradient(135deg, #0f172a, #2563eb)"
else:
    bg = "#0f172a"
    card = "#1e293b"
    text = "#f8fafc"
    input_bg = "#111827"
    border = "#334155"
    hero = "linear-gradient(135deg, #020617, #1d4ed8)"

# CSS
st.markdown(f"""
<style>
.stApp {{
    background: {bg};
    color: {text};
}}

section[data-testid="stSidebar"] {{
    background: #1f2430 !important;
}}

section[data-testid="stSidebar"] * {{
    color: white !important;
}}

.block-container {{
    max-width: 1100px;
    padding-top: 2rem;
}}

.hero {{
    background: {hero};
    color: white;
    padding: 35px;
    border-radius: 26px;
    margin-bottom: 25px;
    box-shadow: 0 15px 35px rgba(0,0,0,0.18);
}}

.logo {{
    font-size: 42px;
    font-weight: 900;
}}

.card {{
    background: {card};
    color: {text};
    padding: 25px;
    border-radius: 22px;
    margin-bottom: 22px;
    border: 1px solid {border};
    box-shadow: 0 10px 25px rgba(15,23,42,0.08);
}}

label, .stTextInput label, .stSelectbox label, .stTextArea label, .stFileUploader label {{
    color: {text} !important;
    font-weight: 700 !important;
    font-size: 15px !important;
}}

input, textarea {{
    background-color: {input_bg} !important;
    color: {text} !important;
    border: 1px solid {border} !important;
}}

[data-testid="stFileUploader"] section {{
    background: #ffffff !important;
    border: 2px dashed #2563eb !important;
    border-radius: 16px !important;
    color: #111827 !important;
}}

[data-testid="stFileUploader"] section * {{
    color: #111827 !important;
}}

[data-testid="stFileUploader"] button {{
    background: #2563eb !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
}}

[data-testid="stFileUploaderFile"] {{
    background: #2563eb !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 8px !important;
    border: none !important;
}}

[data-testid="stFileUploaderFile"] * {{
    color: white !important;
    opacity: 1 !important;
}}

[data-testid="stFileUploaderFile"] span {{
    color: white !important;
    opacity: 1 !important;
}}

[data-testid="stFileUploaderFileName"] {{
    color: white !important;
    font-weight: 800 !important;
    opacity: 1 !important;
}}

div[data-testid="stFileUploaderFile"] {{
    background-color: #2563eb !important;
    border: 2px solid #2563eb !important;
}}

div[data-testid="stFileUploaderFile"] div {{
    color: #ffffff !important;
}}

div[data-testid="stFileUploaderFile"] span {{
    color: #ffffff !important;
}}

div[data-testid="stFileUploaderFile"] small {{
    color: #dbeafe !important;
}}

div[data-testid="stFileUploaderFile"] svg {{
    color: #ffffff !important;
    fill: #ffffff !important;
}}

.stButton > button {{
    background: #2563eb !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.8rem 1.3rem !important;
    font-weight: 800 !important;
    font-size: 16px !important;
}}

.score-box {{
    background: #2563eb;
    color: white;
    padding: 30px;
    border-radius: 24px;
    text-align: center;
}}

.score-number {{
    font-size: 58px;
    font-weight: 900;
    color: white !important;
}}

[data-testid="stMetric"] {{
    background: {card};
    color: {text} !important;
}}

[data-testid="stMetric"] * {{
    color: {text} !important;
}}

.chip-good, .chip-missing, .chip-job, .chip-cv {{
    display: inline-block;
    padding: 9px 14px;
    margin: 5px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 14px;
}}

.chip-good {{
    background: #dcfce7;
    color: #166534;
}}

.chip-missing {{
    background: #fee2e2;
    color: #991b1b;
}}

.chip-job {{
    background: #dbeafe;
    color: #1e40af;
}}

.chip-cv {{
    background: #fef3c7;
    color: #92400e;
}}

.cover-box {{
    background: {input_bg};
    color: {text};
    padding: 22px;
    border-radius: 18px;
    border: 1px solid {border};
    line-height: 1.7;
}}

.stAlert {{
    color: black !important;
    font-weight: 700 !important;
}}

.stAlert * {{
    color: black !important;
    font-weight: 700 !important;
}}

[data-baseweb="notification"] {{
    color: black !important;
}}

[data-baseweb="notification"] * {{
    color: black !important;
}}
</style>
""", unsafe_allow_html=True)

# Read CV files
def read_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def read_docx(file):
    document = docx.Document(file)
    return "\n".join([p.text for p in document.paragraphs])

def get_file_text(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        return read_pdf(uploaded_file)
    elif file_name.endswith(".docx"):
        return read_docx(uploaded_file)
    else:
        return uploaded_file.read().decode("utf-8")

# Text cleaning and matching
def clean_text(text):
    text = text.lower()
    text = text.replace("powerbi", "power bi")
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def skill_found(skill, text):
    return clean_text(skill) in clean_text(text)

def detect_best_field(job_text):
    best_field = None
    best_count = 0

    for field, data in skills_db.items():
        count = sum(1 for skill in data["skills"] if skill_found(skill, job_text))

        if count > best_count:
            best_count = count
            best_field = field

    return best_field, best_count

def analyze_match(cv_text, job_text, selected_field):
    if selected_field == "Auto-detect":
        detected_field, count = detect_best_field(job_text)

        if detected_field is None or count == 0:
            return None, None, None, None, None, None

        field = detected_field

    elif selected_field == "Other":
        return "Other", None, None, None, None, None

    else:
        field = selected_field

    field_skills = skills_db[field]["skills"]

    job_required_skills = [
        skill for skill in field_skills
        if skill_found(skill, job_text)
    ]

    cv_matching_skills = [
        skill for skill in job_required_skills
        if skill_found(skill, cv_text)
    ]

    missing_skills = [
        skill for skill in job_required_skills
        if skill not in cv_matching_skills
    ]

    cv_field_skills = [
        skill for skill in field_skills
        if skill_found(skill, cv_text)
    ]

    score = round((len(cv_matching_skills) / len(job_required_skills)) * 100, 1) if job_required_skills else 0

    return field, score, job_required_skills, cv_matching_skills, missing_skills, cv_field_skills

# Cover letter
def generate_cover_letter(full_name, field, matched_skills, missing_skills):
    strongest_skills = ", ".join(matched_skills[:6]) or "problem solving, attention to detail, communication, and willingness to learn"
    improvement_focus = ", ".join(missing_skills[:3]) or "the key responsibilities of the role"

    return f"""
Dear Hiring Team,

I am excited to apply for this opportunity because it aligns with my skills, career goals, and desire to contribute to meaningful work.

My background in {field} has helped me build a strong foundation in {strongest_skills}. I am confident in my ability to learn quickly, work accurately, solve problems, and contribute positively to your team.

What makes me a strong candidate is my ability to understand requirements, pay attention to detail, and turn tasks into clear outcomes. I am also motivated to keep improving in areas such as {improvement_focus}, while adding value from the beginning.

I would appreciate the opportunity to bring my skills, commitment, and positive attitude to your organisation.

Kind regards,  
{full_name}
"""

def show_chips(items, css_class):
    if not items:
        st.write("Nothing detected.")
    else:
        html = " ".join([f"<span class='{css_class}'>{item}</span>" for item in items])
        st.markdown(html, unsafe_allow_html=True)

# UI
st.markdown("""
<div class="hero">
    <div class="logo">🎓 GradMatch AI</div>
    <p>A professional CV and job matching assistant for graduates from different fields and countries.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)

st.subheader("Your details")

col1, col2 = st.columns(2)

with col1:
    first_name = st.text_input("Enter your first name", placeholder="Example: Nqobile")

    country_options = [
        "South Africa",
        "United States",
        "United Kingdom",
        "Canada",
        "Australia",
        "India",
        "Nigeria",
        "Kenya",
        "Other"
    ]

    selected_country = st.selectbox("Select your country/region", country_options)

    if selected_country == "Other":
        country = st.text_input("Type your country", placeholder="Example: Zimbabwe")
    else:
        country = selected_country

with col2:
    last_name = st.text_input("Enter your last name", placeholder="Example: Sithole")

    selected_field = st.selectbox(
        "Select your field",
        [
            "Auto-detect",
            "Data Analytics / Statistics",
            "IT Support / Technician",
            "Software Development",
            "Finance",
            "Law",
            "Marketing",
            "HR",
            "Engineering",
            "Health Sciences",
            "Education",
            "Business",
            "Other"
        ]
    )

full_name = f"{first_name} {last_name}".strip()

st.subheader("Upload and paste job description")

cv_file = st.file_uploader("Upload your CV here", type=["pdf", "docx", "txt"])

if cv_file is not None:
    st.success(f"CV uploaded successfully: {cv_file.name}")

job_description = st.text_area("Paste the full job description here", height=280)

analyze = st.button("Analyze my match score")

st.markdown("</div>", unsafe_allow_html=True)

# Results
if analyze:
    missing_inputs = []

    if not first_name.strip():
        missing_inputs.append("first name")
    if not last_name.strip():
        missing_inputs.append("last name")
    if not country.strip():
        missing_inputs.append("country")
    if cv_file is None:
        missing_inputs.append("CV upload")
    if not job_description.strip():
        missing_inputs.append("job description")

    if missing_inputs:
        st.warning(
            "Please complete the following before analyzing your match score: "
            + ", ".join(missing_inputs)
            + "."
        )
    else:
        cv_text = get_file_text(cv_file)

        field, score, job_required_skills, cv_matching_skills, missing_skills, cv_field_skills = analyze_match(
            cv_text,
            job_description,
            selected_field
        )

        if field == "Other":
            st.error("Sorry, this field is not supported yet. Please choose one of the available fields.")
        elif field is None:
            st.error("Sorry, the app could not detect a supported field. Please choose the field manually.")
        else:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Your match result")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="score-box">
                    <p>Match Score</p>
                    <div class="score-number">{score}%</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.metric("Field Checked", field)

            with col3:
                st.metric("Missing Skills", len(missing_skills))

            if score >= 75:
                st.success("Strong match. This role looks aligned with your CV.")
            elif score >= 50:
                st.warning("Good potential match. Improve your CV wording before applying.")
            elif score >= 30:
                st.warning("Possible match. You may qualify, but your CV needs stronger alignment.")
            else:
                st.error("Weak match. Your CV does not show enough of the required skills yet.")

            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Skills required by this job")
            show_chips(job_required_skills, "chip-job")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Skills already found in your CV")
            show_chips(cv_matching_skills, "chip-good")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Important skills to add only if they are true")
            show_chips(missing_skills, "chip-missing")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("All field-related skills detected in your CV")
            show_chips(cv_field_skills, "chip-cv")
            st.markdown("</div>", unsafe_allow_html=True)

            cover_letter = generate_cover_letter(
                full_name,
                field,
                cv_matching_skills,
                missing_skills
            )

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Personalised cover letter draft")
            st.markdown(
                f"<div class='cover-box'>{cover_letter.replace(chr(10), '<br>')}</div>",
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)