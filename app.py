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

def load_skills_database():
    with open("skills_database.json", "r") as file:
        return json.load(file)

skills_db = load_skills_database()

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

st.markdown(f"""
<style>
.stApp {{ background: {bg}; color: {text}; }}
section[data-testid="stSidebar"] {{ background: #1f2430 !important; }}
section[data-testid="stSidebar"] * {{ color: white !important; }}
.block-container {{ max-width: 1100px; padding-top: 2rem; }}
.hero {{
    background: {hero};
    color: white;
    padding: 35px;
    border-radius: 26px;
    margin-bottom: 25px;
    box-shadow: 0 15px 35px rgba(0,0,0,0.18);
}}
.logo {{ font-size: 42px; font-weight: 900; }}
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
[data-testid="stFileUploader"] section * {{ color: #111827 !important; }}
[data-testid="stFileUploader"] button {{
    background: #2563eb !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
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
[data-testid="stMetric"] * {{ color: {text} !important; }}
.chip-good, .chip-missing, .chip-job, .chip-cv {{
    display: inline-block;
    padding: 9px 14px;
    margin: 5px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 14px;
}}
.chip-good {{ background: #dcfce7; color: #166534; }}
.chip-missing {{ background: #fee2e2; color: #991b1b; }}
.chip-job {{ background: #dbeafe; color: #1e40af; }}
.chip-cv {{ background: #fef3c7; color: #92400e; }}
.cover-box {{
    background: {input_bg};
    color: {text};
    padding: 22px;
    border-radius: 18px;
    border: 1px solid {border};
    line-height: 1.7;
}}
.stAlert * {{ color: black !important; font-weight: 700 !important; }}
</style>
""", unsafe_allow_html=True)

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
    return uploaded_file.read().decode("utf-8")

def clean_text(text):
    text = text.lower()
    text = text.replace("powerbi", "power bi")
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def found(term, text):
    return clean_text(term) in clean_text(text)

def count_matches(items, text):
    return [item for item in items if found(item, text)]

def related_matches(related_dict, cv_text, job_text):
    matches = []
    missing = []

    for main_skill, related_terms in related_dict.items():
        if found(main_skill, job_text):
            if found(main_skill, cv_text):
                matches.append(main_skill)
            else:
                partial = [term for term in related_terms if found(term, cv_text)]
                if partial:
                    matches.append(f"{main_skill} related to {', '.join(partial[:2])}")
                else:
                    missing.append(main_skill)

    return matches, missing

def detect_best_field(job_text):
    best_field = None
    best_score = 0

    for field, data in skills_db.items():
        score = 0
        score += len(count_matches(data["required_skills"], job_text)) * 3
        score += len(count_matches(data["degrees"], job_text)) * 2
        score += len(count_matches(data["certifications"], job_text)) * 2
        score += len(count_matches(data["soft_skills"], job_text))

        if score > best_score:
            best_score = score
            best_field = field

    return best_field, best_score

def analyze_match(cv_text, job_text, selected_field):
    if selected_field == "Auto-detect":
        field, detected_score = detect_best_field(job_text)
        if field is None or detected_score == 0:
            return None
    elif selected_field == "Other":
        return "Other"
    else:
        field = selected_field

    data = skills_db[field]

    job_required = count_matches(data["required_skills"], job_text)
    cv_required = [skill for skill in job_required if found(skill, cv_text)]
    missing_required = [skill for skill in job_required if skill not in cv_required]

    related_found, related_missing = related_matches(data["related_skills"], cv_text, job_text)

    job_degrees = count_matches(data["degrees"], job_text)
    cv_degrees = [degree for degree in data["degrees"] if found(degree, cv_text)]

    job_certs = count_matches(data["certifications"], job_text)
    cv_certs = [cert for cert in data["certifications"] if found(cert, cv_text)]

    job_soft = count_matches(data["soft_skills"], job_text)
    cv_soft = [skill for skill in job_soft if found(skill, cv_text)]

    required_score = (len(cv_required) / len(job_required) * 45) if job_required else 35
    related_score = (len(related_found) / max(len(related_found) + len(related_missing), 1) * 20)
    degree_score = 20 if cv_degrees else (10 if not job_degrees else 0)
    cert_score = (len(cv_certs) / len(job_certs) * 10) if job_certs else 7
    soft_score = (len(cv_soft) / len(job_soft) * 5) if job_soft else 3

    final_score = round(min(required_score + related_score + degree_score + cert_score + soft_score, 100), 1)

    cv_field_skills = (
        count_matches(data["required_skills"], cv_text)
        + count_matches(data["degrees"], cv_text)
        + count_matches(data["certifications"], cv_text)
        + count_matches(data["soft_skills"], cv_text)
    )

    return {
        "field": field,
        "score": final_score,
        "job_required": job_required,
        "cv_required": cv_required,
        "missing_required": missing_required,
        "related_found": related_found,
        "related_missing": related_missing,
        "cv_degrees": cv_degrees,
        "cv_certs": cv_certs,
        "cv_soft": cv_soft,
        "cv_field_skills": sorted(set(cv_field_skills)),
        "breakdown": {
            "Required skills": round(required_score, 1),
            "Related skills": round(related_score, 1),
            "Degree relevance": round(degree_score, 1),
            "Certifications": round(cert_score, 1),
            "Soft skills": round(soft_score, 1)
        }
    }

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

    selected_country = st.selectbox(
        "Select your country/region",
        ["South Africa", "United States", "United Kingdom", "Canada", "Australia", "India", "Nigeria", "Kenya", "Other"]
    )

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
        st.warning("Please complete the following before analyzing your match score: " + ", ".join(missing_inputs) + ".")
    else:
        cv_text = get_file_text(cv_file)
        result = analyze_match(cv_text, job_description, selected_field)

        if result == "Other":
            st.error("Sorry, this field is not supported yet. Please choose one of the available fields.")
        elif result is None:
            st.error("Sorry, the app could not detect a supported field. Please choose the field manually.")
        else:
            field = result["field"]
            score = result["score"]

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Your match result")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="score-box">
                    <p>ATS-Style Match Score</p>
                    <div class="score-number">{score}%</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.metric("Field Checked", field)

            with col3:
                st.metric("Missing Required Skills", len(result["missing_required"]))

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
            st.subheader("Score breakdown")
            for label, value in result["breakdown"].items():
                st.write(f"{label}: {value}")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Required skills found in your CV")
            show_chips(result["cv_required"], "chip-good")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Related skills found")
            show_chips(result["related_found"], "chip-cv")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Important required skills to add only if they are true")
            show_chips(result["missing_required"], "chip-missing")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Degrees detected in your CV")
            show_chips(result["cv_degrees"], "chip-job")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Certifications detected in your CV")
            show_chips(result["cv_certs"], "chip-job")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("All field-related items detected in your CV")
            show_chips(result["cv_field_skills"], "chip-cv")
            st.markdown("</div>", unsafe_allow_html=True)

            cover_letter = generate_cover_letter(
                full_name,
                field,
                result["cv_required"] + result["related_found"],
                result["missing_required"]
            )

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Personalised cover letter draft")
            st.markdown(
                f"<div class='cover-box'>{cover_letter.replace(chr(10), '<br>')}</div>",
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)
