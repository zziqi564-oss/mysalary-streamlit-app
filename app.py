#导入数据
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
df_raw = pd.read_excel("Salary_Data.xlsx")
matplotlib.rcParams['figure.dpi'] = 120
#删除缺失值
df = df_raw.dropna().copy()
#清洗数据
edu_map = {
    "Bachelor's": "Bachelor's",
    "Bachelor's Degree": "Bachelor's",
    "Master's": "Master's",
    "Master's Degree": "Master's",
    "PhD": "PhD",
    "phD": "PhD",
    "High School": "High School"
}
df["Education Level"] = df["Education Level"].map(edu_map)
df = df.dropna(subset=["Education Level"])
#移除salary的异常值
df = df[df["Salary"] >= 10000]
#职位分类
def categorise_job(title):
    t = title.lower()
    if any(w in t for w in ["software", "developer", "engineer", "full stack", "front end", "back end"]):
        return "Software Engineering"
    elif any(w in t for w in ["data scientist", "data analyst", "data engineer", "business intelligence"]):
        return "Data & Analytics"
    elif any(w in t for w in ["marketing", "content", "social media", "seo"]):
        return "Marketing"
    elif any(w in t for w in ["financial", "accountant", "finance"]):
        return "Finance & Accounting"
    elif any(w in t for w in ["product manager", "project manager", "project engineer"]):
        return "Product & Project Mgmt"
    elif any(w in t for w in ["sales", "business develop", "account manager"]):
        return "Sales & Business Dev"
    elif any(w in t for w in ["human resource", "hr ", "recruiter", "talent"]):
        return "Human Resources"
    elif any(w in t for w in ["operations", "supply chain", "logistics"]):
        return "Operations"
    elif any(w in t for w in ["director", "ceo", "cto", "cfo", "vp ", "vice president", "chief"]):
        return "Executive / Leadership"
    elif any(w in t for w in ["manager", "senior"]):
        return "Management"
    else:
        return "Other"

df["Job Category"] = df["Job Title"].apply(categorise_job)
#划分就业年数
df["Experience Level"] = pd.cut(
    df["Years of Experience"],
    bins=[0, 2, 5, 10, 50],
    labels=["Entry (0-2yr)", "Junior (3-5yr)", "Mid (6-10yr)", "Senior (10+yr)"]
)
#分析数据-职业
# Top 15 most common job titles
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Bar chart of top jobs
top15 = df["Job Title"].value_counts().head(15)
top15.plot(kind="barh", ax=axes[0], color="#4C78A8")
axes[0].set_title("Top 15 Most Common Job Titles")
axes[0].set_xlabel("Count")
axes[0].invert_yaxis()

# Pie chart of job categories
cat_counts = df["Job Category"].value_counts()
cat_counts.plot(kind="pie", ax=axes[1], autopct="%1.1f%%", startangle=90, pctdistance=0.85)
axes[1].set_title("Distribution by Job Category")
axes[1].set_ylabel("")

plt.tight_layout()
plt.show()
print("\nKey finding: Software Engineering and Marketing are the two largest categories.")
#分析数据-教育和经历影响薪资
# Salary distribution by education level
edu_order = ["High School", "Bachelor's", "Master's", "PhD"]
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Box plot: salary by education
edu_data = [df[df["Education Level"] == e]["Salary"] for e in edu_order]
bp = axes[0].boxplot(edu_data, labels=edu_order, patch_artist=True)
colors = ["#E45756", "#4C78A8", "#F58518", "#72B7B2"]
for patch, color in zip(bp["boxes"], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
axes[0].set_title("Salary Distribution by Education Level")
axes[0].set_ylabel("Salary ($)")

# Scatter plot: experience vs salary coloured by education
for i, edu in enumerate(edu_order):
    subset = df[df["Education Level"] == edu]
    axes[1].scatter(subset["Years of Experience"], subset["Salary"],
                    alpha=0.3, label=edu, s=10, color=colors[i])
axes[1].set_title("Experience vs Salary (by Education)")
axes[1].set_xlabel("Years of Experience")
axes[1].set_ylabel("Salary ($)")
axes[1].legend(fontsize=8)

plt.tight_layout()
plt.show()

# Summary statistics
print("Median salary by education level:")
for edu in edu_order:
    median_sal = df[df["Education Level"] == edu]["Salary"].median()
    print(f"  {edu:15s}: ${median_sal:>10,.0f}")
#分析数据-职业影响薪资
# Average and median salary by job category
cat_salary = df.groupby("Job Category")["Salary"].agg(["mean", "median", "count"])
cat_salary.columns = ["Mean Salary", "Median Salary", "Count"]
cat_salary = cat_salary.sort_values("Median Salary", ascending=True)

fig, ax = plt.subplots(figsize=(10, 5))
y_pos = range(len(cat_salary))
ax.barh(y_pos, cat_salary["Median Salary"], color="#4C78A8", alpha=0.7, label="Median")
ax.barh(y_pos, cat_salary["Mean Salary"], color="#F58518", alpha=0.4, label="Mean")
ax.set_yticks(y_pos)
ax.set_yticklabels(cat_salary.index, fontsize=9)
ax.set_xlabel("Salary ($)")
ax.set_title("Mean vs Median Salary by Job Category")
ax.legend()

plt.tight_layout()
plt.show()

print("\nSalary summary by category:")
print(cat_salary.to_string())
#分析数据-学历和经历影响薪资
# Heatmap of average salary by education and experience level
heatmap_data = df.groupby(["Education Level", "Experience Level"])["Salary"].mean().reset_index()
heatmap_pivot = heatmap_data.pivot(index="Education Level", columns="Experience Level", values="Salary")
heatmap_pivot = heatmap_pivot.reindex(edu_order)

fig, ax = plt.subplots(figsize=(10, 4))
im = ax.imshow(heatmap_pivot.values, cmap="YlOrRd", aspect="auto")

# Labels
ax.set_xticks(range(len(heatmap_pivot.columns)))
ax.set_xticklabels(heatmap_pivot.columns, fontsize=9)
ax.set_yticks(range(len(heatmap_pivot.index)))
ax.set_yticklabels(heatmap_pivot.index, fontsize=9)

# Add value annotations
for i in range(len(heatmap_pivot.index)):
    for j in range(len(heatmap_pivot.columns)):
        val = heatmap_pivot.iloc[i, j]
        if pd.notna(val):
            ax.text(j, i, f"${val:,.0f}", ha="center", va="center", fontsize=8, fontweight="bold")

plt.colorbar(im, ax=ax, label="Average Salary ($)")
ax.set_title("Average Salary: Education Level × Experience Level")

plt.tight_layout()
plt.show()

print("\nKey finding: The salary premium for higher education is most visible at senior experience levels.")
#技能分析
from collections import Counter

def map_skills(title):
    """Map job titles to commonly required skills based on industry knowledge."""
    t = title.lower()
    skills = []
    if any(w in t for w in ["software", "developer", "full stack", "front end", "back end", "engineer"]):
        skills.extend(["Python", "JavaScript", "Git", "SQL", "Problem Solving"])
    if "front end" in t:
        skills.extend(["HTML/CSS", "React", "UI Design"])
    if "back end" in t:
        skills.extend(["API Design", "Database", "Cloud"])
    if "data scientist" in t:
        skills.extend(["Python", "Machine Learning", "Statistics", "SQL", "Data Visualisation"])
    if "data analyst" in t:
        skills.extend(["SQL", "Excel", "Python", "Data Visualisation", "Statistics"])
    if any(w in t for w in ["marketing"]):
        skills.extend(["Digital Marketing", "Analytics", "Communication", "Content Strategy"])
    if any(w in t for w in ["financial", "accountant", "finance"]):
        skills.extend(["Excel", "Financial Analysis", "Accounting", "ERP Systems"])
    if any(w in t for w in ["product manager"]):
        skills.extend(["Product Strategy", "Agile", "Communication", "Data Analysis", "UX"])
    if any(w in t for w in ["project manager", "project engineer"]):
        skills.extend(["Project Planning", "Agile", "Communication", "Risk Management"])
    if any(w in t for w in ["sales", "business develop"]):
        skills.extend(["Negotiation", "CRM", "Communication", "Presentation"])
    if any(w in t for w in ["manager", "director", "senior", "lead", "chief", "vp "]):
        skills.extend(["Leadership", "Strategic Thinking", "Team Management"])
    if not skills:
        skills.extend(["Communication", "Problem Solving", "Teamwork"])
    return list(set(skills))

df["Skills"] = df["Job Title"].apply(map_skills)

# Count all skills
all_skills = []
for s_list in df["Skills"]:
    all_skills.extend(s_list)

skill_counts = Counter(all_skills)
top20 = pd.DataFrame(skill_counts.most_common(20), columns=["Skill", "Frequency"])

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(top20["Skill"], top20["Frequency"], color="#2A9D8F")
ax.invert_yaxis()
ax.set_title("Top 20 Most In-Demand Skills")
ax.set_xlabel("Frequency (number of job postings)")
plt.tight_layout()
plt.show()

# Average salary per skill
skill_salary = {}
for _, row in df.iterrows():
    for skill in row["Skills"]:
        if skill not in skill_salary:
            skill_salary[skill] = []
        skill_salary[skill].append(row["Salary"])

skill_sal_df = pd.DataFrame([
    {"Skill": skill, "Avg Salary": sum(sals)/len(sals), "Count": len(sals)}
    for skill, sals in skill_salary.items()
    if len(sals) >= 20
]).sort_values("Avg Salary", ascending=True)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(skill_sal_df["Skill"], skill_sal_df["Avg Salary"], color="#E76F51")
ax.set_title("Average Salary by Skill (min 20 records)")
ax.set_xlabel("Average Salary ($)")
# Add value labels
for bar in bars:
    width = bar.get_width()
    ax.text(width + 1000, bar.get_y() + bar.get_height()/2,
            f"${width:,.0f}", ha="left", va="center", fontsize=7)

plt.tight_layout()
plt.show()

print("\nKey finding: Technical skills like Cloud, API Design, and Machine Learning")
print("are associated with the highest average salaries.")


#Streamlit
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Career Planning Dashboard Based on Job Posting Data", layout="wide")
st.title("Career Planning Dashboard Based on Job Posting Data")

def clean_data(df):
    # 删除缺失值
    df = df.dropna().copy()
    
    # 清洗教育程度
    edu_map = {
        "Bachelor's": "Bachelor's",
        "Bachelor's Degree": "Bachelor's",
        "Master's": "Master's",
        "Master's Degree": "Master's",
        "PhD": "PhD",
        "phD": "PhD",
        "High School": "High School"
    }
    df["Education Level"] = df["Education Level"].map(edu_map)
    df = df.dropna(subset=["Education Level"])
    
    # 移除薪资异常值
    df = df[df["Salary"] >= 10000]
    
    # 职位分类函数
    def categorise_job(title):
        t = title.lower()
        if any(w in t for w in ["software", "developer", "engineer", "full stack", "front end", "back end"]):
            return "Software Engineering"
        elif any(w in t for w in ["data scientist", "data analyst", "data engineer", "business intelligence"]):
            return "Data & Analytics"
        elif any(w in t for w in ["marketing", "content", "social media", "seo"]):
            return "Marketing"
        elif any(w in t for w in ["financial", "accountant", "finance"]):
            return "Finance & Accounting"
        elif any(w in t for w in ["product manager", "project manager", "project engineer"]):
            return "Product & Project Mgmt"
        elif any(w in t for w in ["sales", "business develop", "account manager"]):
            return "Sales & Business Dev"
        elif any(w in t for w in ["human resource", "hr ", "recruiter", "talent"]):
            return "Human Resources"
        elif any(w in t for w in ["operations", "supply chain", "logistics"]):
            return "Operations"
        elif any(w in t for w in ["director", "ceo", "cto", "cfo", "vp ", "vice president", "chief"]):
            return "Executive / Leadership"
        elif any(w in t for w in ["manager", "senior"]):
            return "Management"
        else:
            return "Other"
    
    df["Job Category"] = df["Job Title"].apply(categorise_job)
    
    # 划分经验年数
    df["Experience Level"] = pd.cut(
        df["Years of Experience"],
        bins=[0, 2, 5, 10, 50],
        labels=["Entry (0-2yr)", "Junior (3-5yr)", "Mid (6-10yr)", "Senior (10+yr)"]
    )
    
    # 技能分析函数
    def map_skills(title):
        t = title.lower()
        skills = []
        if any(w in t for w in ["software", "developer", "full stack", "front end", "back end", "engineer"]):
            skills.extend(["Python", "JavaScript", "Git", "SQL", "Problem Solving"])
        if "front end" in t:
            skills.extend(["HTML/CSS", "React", "UI Design"])
        if "back end" in t:
            skills.extend(["API Design", "Database", "Cloud"])
        if "data scientist" in t:
            skills.extend(["Python", "Machine Learning", "Statistics", "SQL", "Data Visualisation"])
        if "data analyst" in t:
            skills.extend(["SQL", "Excel", "Python", "Data Visualisation", "Statistics"])
        if any(w in t for w in ["marketing"]):
            skills.extend(["Digital Marketing", "Analytics", "Communication", "Content Strategy"])
        if any(w in t for w in ["financial", "accountant", "finance"]):
            skills.extend(["Excel", "Financial Analysis", "Accounting", "ERP Systems"])
        if any(w in t for w in ["product manager"]):
            skills.extend(["Product Strategy", "Agile", "Communication", "Data Analysis", "UX"])
        if any(w in t for w in ["project manager", "project engineer"]):
            skills.extend(["Project Planning", "Agile", "Communication", "Risk Management"])
        if any(w in t for w in ["sales", "business develop"]):
            skills.extend(["Negotiation", "CRM", "Communication", "Presentation"])
        if any(w in t for w in ["manager", "director", "senior", "lead", "chief", "vp "]):
            skills.extend(["Leadership", "Strategic Thinking", "Team Management"])
        if not skills:
            skills.extend(["Communication", "Problem Solving", "Teamwork"])
        return list(set(skills))
    
    df["Skills"] = df["Job Title"].apply(map_skills)
    
    return df

# ==================== 可视化函数 ====================
def make_chart(df):
    matplotlib.rcParams['figure.dpi'] = 120
    figs = {}
    
    # 图1: 职位分布 (Top 15 + 分类饼图)
    fig1, axes = plt.subplots(1, 2, figsize=(14, 5))
    top15 = df["Job Title"].value_counts().head(15)
    top15.plot(kind="barh", ax=axes[0], color="#4C78A8")
    axes[0].set_title("Top 15 Most Common Job Titles")
    axes[0].set_xlabel("Count")
    axes[0].invert_yaxis()
    
    cat_counts = df["Job Category"].value_counts()
    cat_counts.plot(kind="pie", ax=axes[1], autopct="%1.1f%%", startangle=90, pctdistance=0.85)
    axes[1].set_title("Distribution by Job Category")
    axes[1].set_ylabel("")
    plt.tight_layout()
    figs['job_distribution'] = fig1
    
    # 图2: 教育程度 vs 薪资
    edu_order = ["High School", "Bachelor's", "Master's", "PhD"]
    fig2, axes = plt.subplots(1, 2, figsize=(14, 5))
    edu_data = [df[df["Education Level"] == e]["Salary"] for e in edu_order]
    bp = axes[0].boxplot(edu_data, labels=edu_order, patch_artist=True)
    colors = ["#E45756", "#4C78A8", "#F58518", "#72B7B2"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    axes[0].set_title("Salary Distribution by Education Level")
    axes[0].set_ylabel("Salary ($)")
    
    for i, edu in enumerate(edu_order):
        subset = df[df["Education Level"] == edu]
        axes[1].scatter(subset["Years of Experience"], subset["Salary"],
                        alpha=0.3, label=edu, s=10, color=colors[i])
    axes[1].set_title("Experience vs Salary (by Education)")
    axes[1].set_xlabel("Years of Experience")
    axes[1].set_ylabel("Salary ($)")
    axes[1].legend(fontsize=8)
    plt.tight_layout()
    figs['salary_education'] = fig2
    
    # 图3: 职业类别薪资对比
    cat_salary = df.groupby("Job Category")["Salary"].agg(["mean", "median", "count"])
    cat_salary.columns = ["Mean Salary", "Median Salary", "Count"]
    cat_salary = cat_salary.sort_values("Median Salary", ascending=True)
    
    fig3, ax = plt.subplots(figsize=(10, 5))
    y_pos = range(len(cat_salary))
    ax.barh(y_pos, cat_salary["Median Salary"], color="#4C78A8", alpha=0.7, label="Median")
    ax.barh(y_pos, cat_salary["Mean Salary"], color="#F58518", alpha=0.4, label="Mean")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(cat_salary.index, fontsize=9)
    ax.set_xlabel("Salary ($)")
    ax.set_title("Mean vs Median Salary by Job Category")
    ax.legend()
    plt.tight_layout()
    figs['salary_by_category'] = fig3
    
    # 图4: 热力图 - 学历 × 经验水平
    heatmap_data = df.groupby(["Education Level", "Experience Level"])["Salary"].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index="Education Level", columns="Experience Level", values="Salary")
    heatmap_pivot = heatmap_pivot.reindex(edu_order)
    
    fig4, ax = plt.subplots(figsize=(10, 4))
    im = ax.imshow(heatmap_pivot.values, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(heatmap_pivot.columns)))
    ax.set_xticklabels(heatmap_pivot.columns, fontsize=9)
    ax.set_yticks(range(len(heatmap_pivot.index)))
    ax.set_yticklabels(heatmap_pivot.index, fontsize=9)
    for i in range(len(heatmap_pivot.index)):
        for j in range(len(heatmap_pivot.columns)):
            val = heatmap_pivot.iloc[i, j]
            if pd.notna(val):
                ax.text(j, i, f"${val:,.0f}", ha="center", va="center", fontsize=8, fontweight="bold")
    plt.colorbar(im, ax=ax, label="Average Salary ($)")
    ax.set_title("Average Salary: Education Level × Experience Level")
    plt.tight_layout()
    figs['salary_heatmap'] = fig4
    
    # 图5: Top 20 技能需求
    all_skills = []
    for s_list in df["Skills"]:
        all_skills.extend(s_list)
    skill_counts = Counter(all_skills)
    top20 = pd.DataFrame(skill_counts.most_common(20), columns=["Skill", "Frequency"])
    
    fig5, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top20["Skill"], top20["Frequency"], color="#2A9D8F")
    ax.invert_yaxis()
    ax.set_title("Top 20 Most In-Demand Skills")
    ax.set_xlabel("Frequency (number of job postings)")
    plt.tight_layout()
    figs['top_skills'] = fig5
    
    # 图6: 技能平均薪资
    skill_salary = {}
    for _, row in df.iterrows():
        for skill in row["Skills"]:
            if skill not in skill_salary:
                skill_salary[skill] = []
            skill_salary[skill].append(row["Salary"])
    
    skill_sal_df = pd.DataFrame([
        {"Skill": skill, "Avg Salary": sum(sals)/len(sals), "Count": len(sals)}
        for skill, sals in skill_salary.items()
        if len(sals) >= 20
    ]).sort_values("Avg Salary", ascending=True)
    
    fig6, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(skill_sal_df["Skill"], skill_sal_df["Avg Salary"], color="#E76F51")
    ax.set_title("Average Salary by Skill (min 20 records)")
    ax.set_xlabel("Average Salary ($)")
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1000, bar.get_y() + bar.get_height()/2,
                f"${width:,.0f}", ha="left", va="center", fontsize=7)
    plt.tight_layout()
    figs['skill_salary'] = fig6
    
    return figs, cat_salary, edu_order

# 1️⃣ 数据获取
uploaded_file = st.file_uploader("Upload data file", type=["csv", "xlsx"])

if uploaded_file:
    # 根据文件扩展名选择读取方式
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)  # ✅ 用 Excel 方式读取
else:
     # 如果没有上传文件，自动加载默认数据
    default_file = "Salary_Data.xlsx"
    try:
        df = pd.read_excel(default_file)
        st.info(f"Using default data file: {default_file}")
    except FileNotFoundError:
        st.error(f"Default file '{default_file}' not found. Please upload a file.")
        st.stop()

# 2️⃣ 清洗（可加进度提示）
with st.spinner("Cleaning..."):
    df_clean = clean_data(df)

st.success("Cleaning complete")
st.write("Preview:", df_clean.head())

# 3️⃣ 分析 & 可视化
# ==================== 互动筛选器 ====================
st.sidebar.header("🔍 Filter Data")

# 删除经验水平为空的行（避免排序错误）
df_clean = df_clean.dropna(subset=["Experience Level"])

# 1️⃣ 薪资范围筛选
min_salary = st.sidebar.slider(
    "💰 Minimum Salary ($)",
    min_value=int(df_clean["Salary"].min()),
    max_value=int(df_clean["Salary"].max()),
    value=int(df_clean["Salary"].min()),
    step=5000
)

max_salary = st.sidebar.slider(
    "💰 Maximum Salary ($)",
    min_value=int(df_clean["Salary"].min()),
    max_value=int(df_clean["Salary"].max()),
    value=int(df_clean["Salary"].max()),
    step=5000
)

# 2️⃣ 职位类别筛选
selected_categories = st.sidebar.multiselect(
    "📁 Job Categories",
    options=sorted(df_clean["Job Category"].unique()),
    default=sorted(df_clean["Job Category"].unique())
)

# 3️⃣ 教育程度筛选
selected_education = st.sidebar.multiselect(
    "🎓 Education Level",
    options=sorted(df_clean["Education Level"].unique()),
    default=sorted(df_clean["Education Level"].unique())
)

# 4️⃣ 经验年数筛选（过滤掉 NaN）
experience_options = sorted([x for x in df_clean["Experience Level"].unique() if pd.notna(x)])
selected_experience = st.sidebar.multiselect(
    "📊 Experience Level",
    options=experience_options,
    default=experience_options
)

# 应用所有筛选条件
df_filtered = df_clean.copy()
df_filtered = df_filtered[(df_filtered["Salary"] >= min_salary) & (df_filtered["Salary"] <= max_salary)]

if selected_categories:
    df_filtered = df_filtered[df_filtered["Job Category"].isin(selected_categories)]

if selected_education:
    df_filtered = df_filtered[df_filtered["Education Level"].isin(selected_education)]

if selected_experience:
    df_filtered = df_filtered[df_filtered["Experience Level"].isin(selected_experience)]

# 显示筛选后的记录数
st.sidebar.markdown("---")
st.sidebar.metric("📊 Records After Filtering", len(df_filtered))

if len(df_filtered) == 0:
    st.warning("No data matches the selected filters. Please adjust your filter criteria.")
    st.stop()
if len(df_filtered) == 0:
    st.warning("No data matches the selected filters. Please adjust your filter criteria.")
    st.stop()

# ==================== 显示图表 ====================
st.subheader("📈 Analysis Results")

with st.spinner("Generating charts..."):
    figs, cat_salary, edu_order = make_chart(df_filtered)

# 显示所有图表
st.subheader("📊 1. Job Distribution & Salary by Education")
col1, col2 = st.columns(2)
with col1:
    st.pyplot(figs['job_distribution'])
with col2:
    st.pyplot(figs['salary_education'])

st.subheader("💰 2. Salary by Job Category")
st.pyplot(figs['salary_by_category'])

st.subheader("🔥 3. Salary Heatmap (Education × Experience)")
st.pyplot(figs['salary_heatmap'])

st.subheader("🛠️ 4. Skills Analysis")
col1, col2 = st.columns(2)
with col1:
    st.pyplot(figs['top_skills'])
with col2:
    st.pyplot(figs['skill_salary'])

# 关键发现
st.subheader("🔑 Key Findings")
st.markdown("""
- **Software Engineering** and **Marketing** are the two largest job categories
- The salary premium for higher education is most visible at senior experience levels
- Technical skills like **Cloud, API Design, and Machine Learning** are associated with the highest average salaries
""")

# 显示薪资统计表
with st.expander("📋 View Detailed Salary Statistics by Category"):
    st.dataframe(cat_salary)

# 显示筛选后的数据
st.subheader("📋 Filtered Data")
st.dataframe(df_filtered)