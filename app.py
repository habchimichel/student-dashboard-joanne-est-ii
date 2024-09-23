import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load data
data_path = r'Overall_Averages.xlsx'
df = pd.read_excel(data_path)

# Define maximum scores for the columns (assuming similar columns to CODE 1)
max_scores = {
    "EST I total": 1600,
    "EST I - Literacy": 800,
    "EST I - Mathematics": 800,
    "EST I - Essay": 8,
    "EST II - Biology": 80,
    "EST II - Physics": 75,
    "EST II - Chemistry": 85,
    "EST II - Math 1": 50,
    "EST II - Math 2": 50,
    "EST II - Literature": 60,
    "EST II - World History": 65,
    "EST II - Economics": 60
}

# Function to wrap text at spaces for long skill names
def wrap_text(text, max_length=35):
    # Remove unwanted prefixes before wrapping
    text = text.replace('A-SK-', '').replace('B-SK-', '').replace('C-SK-', '').replace('D-SK-', '')
    text = text.replace('A-', '').replace('B-', '').replace('C-', '').replace('D-', '')

    words = text.split()
    lines = []
    line = ""

    for word in words:
        if len(line) + len(word) + 1 <= max_length:
            if line:
                line += " "
            line += word
        else:
            lines.append(line)
            line = word

    if line:
        lines.append(line)

    return '<br>'.join(lines)

# Function to create a gauge plot for each skill
def create_gauge(skill, average_score, max_score):
    percentage_score = average_score * 100 / max_score

    # Determine the color based on percentage score
    bar_color = 'blue'
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage_score,
        number={'font': {'size': 24}},
        title={'text': wrap_text(skill), 'font': {'size': 14}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': bar_color}
        }
    ))

    return fig

# Streamlit App Layout
st.title("Student Performance Dashboard")

# Filters
student_search = st.selectbox("Search for a student by username", options=df['Username'].unique())
selected_tests = st.multiselect("Select Test(s)", options=df['Test'].unique())
selected_countries = st.multiselect("Select Country(ies)", options=df['Country'].unique())
selected_versions = st.multiselect("Select Test Version(s)", options=['Select All Versions'] + df['Version'].unique().tolist())

# Apply "Select All Versions" filter logic
if 'Select All Versions' in selected_versions:
    selected_versions = df['Version'].unique().tolist()

# Filter data based on selections
filtered_df = df

if student_search:
    filtered_df = filtered_df[filtered_df['Username'] == student_search]

if selected_tests:
    filtered_df = filtered_df[filtered_df['Test'].isin(selected_tests)]

if selected_countries:
    filtered_df = filtered_df[filtered_df['Country'].isin(selected_countries)]

if selected_versions:
    filtered_df = filtered_df[filtered_df['Version'].isin(selected_versions)]

# Display Gauges for each skill in the filtered dataframe
st.header("Skill Performance Gauges")

if not filtered_df.empty:
    for test in filtered_df['Test'].unique():
        st.subheader(test)
        test_df = filtered_df[filtered_df['Test'] == test]
        skill_columns = st.columns(len(test_df['Skill/Passage'].unique()))  # Create dynamic columns based on the number of skills
        
        for idx, skill in enumerate(test_df['Skill/Passage'].unique()):
            skill_row = test_df[test_df['Skill/Passage'] == skill].iloc[0]
            average_score = skill_row['Average Score']
            max_score = max_scores.get(test, 100)  # Adjust based on available max scores
            with skill_columns[idx]:
                st.plotly_chart(create_gauge(skill, average_score, max_score), use_container_width=True)

# Totals Section
st.header("Total Averages")
skill_totals = {}
non_skill_totals = {}

# Accumulate scores for skills and non-skills separately
for _, row in filtered_df.iterrows():
    skill_passage = row['Skill/Passage']
    average_score = row['Average Score']
    percentage_score = average_score * 100 / max_scores.get(row['Test'], 100)

    clean_title = skill_passage.replace('A-SK-', '').replace('B-SK-', '').replace('C-SK-', '').replace('D-SK-', '') \
                               .replace('A-', '').replace('B-', '').replace('C-', '').replace('D-', '')

    if '-SK-' in skill_passage:
        if clean_title in skill_totals:
            skill_totals[clean_title]['total_score'] += percentage_score
            skill_totals[clean_title]['count'] += 1
        else:
            skill_totals[clean_title] = {'total_score': percentage_score, 'count': 1}
    else:
        if clean_title in non_skill_totals:
            non_skill_totals[clean_title]['total_score'] += percentage_score
            non_skill_totals[clean_title]['count'] += 1
        else:
            non_skill_totals[clean_title] = {'total_score': percentage_score, 'count': 1}

# Calculate average score for each skill and non-skill
avg_skill_scores = {title: data['total_score'] / data['count'] for title, data in skill_totals.items()}
avg_non_skill_scores = {title: data['total_score'] / data['count'] for title, data in non_skill_totals.items()}

# Display totals for skills
st.subheader("Skill Averages")
for title, avg_score in avg_skill_scores.items():
    st.write(f"Skill: {title} - Average: {avg_score:.2f}%")

# Display totals for non-skills
st.subheader("Non-Skill Averages")
for title, avg_score in avg_non_skill_scores.items():
    st.write(f"Non-Skill: {title} - Average: {avg_score:.2f}%")
