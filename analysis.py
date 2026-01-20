import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# Set working directory safely
if "__file__" in globals():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load enrolment data
enrolment_files = glob.glob("api_data_aadhar_enrolment_*.csv")
enrolment_df = pd.concat([pd.read_csv(f) for f in enrolment_files], ignore_index=True)

# Load biometric update data
biometric_files = glob.glob("api_data_aadhar_biometric_*.csv")
biometric_df = pd.concat([pd.read_csv(f) for f in biometric_files], ignore_index=True)

# Load demographic update data
demographic_files = glob.glob("api_data_aadhar_demographic_*.csv")
demographic_df = pd.concat([pd.read_csv(f) for f in demographic_files], ignore_index=True)

# Convert date columns to datetime
enrolment_df['date'] = pd.to_datetime(enrolment_df['date'], dayfirst=True, errors='coerce')
biometric_df['date'] = pd.to_datetime(biometric_df['date'], dayfirst=True, errors='coerce')
demographic_df['date'] = pd.to_datetime(demographic_df['date'], dayfirst=True, errors='coerce')

# Sort data by date
enrolment_df = enrolment_df.sort_values('date')
biometric_df = biometric_df.sort_values('date')
demographic_df = demographic_df.sort_values('date')

# Total enrolment over time
enrolment_df['total_enrolment'] = (
    enrolment_df['age_0_5'] +
    enrolment_df['age_5_17'] +
    enrolment_df['age_18_greater']
)

enrolment_trend = enrolment_df.groupby('date')['total_enrolment'].sum()

plt.figure()
enrolment_trend.plot()
plt.title("Total Aadhaar Enrolment Over Time")
plt.xlabel("Date")
plt.ylabel("Number of Enrolments")
plt.tight_layout()
plt.savefig("figure_1_total_enrolment.png", dpi=300)
plt.show()

# Total biometric updates
biometric_df['total_biometric_updates'] = (
    biometric_df['bio_age_5_17'] +
    biometric_df['bio_age_17_']
)
biometric_trend = biometric_df.groupby('date')['total_biometric_updates'].sum()

# Total demographic updates
demographic_df['total_demographic_updates'] = (
    demographic_df['demo_age_5_17'] +
    demographic_df['demo_age_17_']
)
demographic_trend = demographic_df.groupby('date')['total_demographic_updates'].sum()

plt.figure()
biometric_trend.plot(label="Biometric Updates")
demographic_trend.plot(label="Demographic Updates")
plt.title("Aadhaar Update Requests Over Time")
plt.xlabel("Date")
plt.ylabel("Number of Updates")
plt.legend()
plt.tight_layout()
plt.savefig("figure_2_updates_over_time.png", dpi=300)
plt.show()

# Top 5 states by enrolment
state_enrolment = enrolment_df.groupby('state')['total_enrolment'].sum()
top5_states = state_enrolment.sort_values(ascending=False).head(5)

plt.figure()
top5_states.plot(kind='bar')
plt.title("Top 5 States by Aadhaar Enrolment")
plt.xlabel("State")
plt.ylabel("Total Enrolments")
plt.tight_layout()
plt.savefig("figure_3_top5_states_enrolment.png", dpi=300)
plt.show()

# State-wise total updates
state_bio_updates = biometric_df.groupby('state')['total_biometric_updates'].sum()
state_demo_updates = demographic_df.groupby('state')['total_demographic_updates'].sum()

state_total_updates = state_bio_updates.add(state_demo_updates, fill_value=0)

# Align enrolment and updates
state_analysis = pd.DataFrame({
    'total_enrolments': state_enrolment,
    'total_updates': state_total_updates
}).fillna(0).sort_index()

# Update-to-Enrolment Ratio (Capacity Stress Indicator)
state_analysis['update_to_enrol_ratio'] = (
    state_analysis['total_updates'] /
    (state_analysis['total_enrolments'] + 1)
)

# Top stressed states
top_stress_states = state_analysis.sort_values(
    'update_to_enrol_ratio', ascending=False
).head(10)

print(top_stress_states)

plt.figure()
top_stress_states['update_to_enrol_ratio'].plot(kind='barh')
plt.title("States with Highest Aadhaar Update-to-Enrolment Pressure")
plt.xlabel("Update-to-Enrolment Ratio")
plt.ylabel("State")
plt.tight_layout()
plt.savefig("figure_5_update_enrol_pressure.png", dpi=300)
plt.show()



