import re
import pandas as pd

# Reinitialize the raw data
data = """
Gammøn UTC -7 — 8/3/2025 12:48 PM
2025-08-03; RV-DC-FTS-03 The Eternal Order; 2.5HRs
Bloo37 (UTC -5/US Central) — 8/5/2025 4:46 PM
2025-08-4; Menace Under Otari (Part 1); 3 Hours
Varvatos Vex (UTC -7) — 8/5/2025 6:48 PM
2025-08-04; Out of the Abyss (Session Sixty-Five); 3 hours
DigitalMatt (UTC-5/EST) — 8/7/2025 10:53 PM
2025-08-07; FR-DC-MELB-01-06 Syncopated Denouement; 3 hours
Gammøn UTC -7 — 8/10/2025 1:22 PM
2025-08-08; AD&D2ePbP Lords of Darkness Week Four; 1HR
Varvatos Vex (UTC -7) — 8/13/2025 7:50 PM
2025-08-12; Out of the Abyss (Session Sixty-Six); 3 hours
Gammøn UTC -7 — 8/15/2025 2:09 AM
2025--08-14; Volo Back the Dead PbP Finale; 4HRs
sterling UTC-6 — 8/16/2025 10:23 AM
2025-08-15; Ad Astra: Lone Survivors Part 1, 2.5 hrs
Gammøn UTC -7 — 8/17/2025 1:30 PM
2025-08-15; AD&D2ePbP Lords of  Darkness Week Five; 1HR
Gammøn UTC -7 — 8/17/2025 1:30 PM
2025-08-17; FTS04 The Eye of Ezra; 2.5HRs
Varvatos Vex (UTC -7) — 8/20/2025 5:22 PM
2025-08-18; Out of the Abyss (Session Sixty-Seven); 3.5 hours 
Bloo37 (UTC -5/US Central) — 8/20/2025 7:39 PM
2025-08-18; Menace Under Otari (Part 2); 3 Hours
sterling UTC-6 — 8/23/2025 12:25 AM
2025-08-22: Ad Astra Lone Survivors part 2, 3.5 hrs
Gammøn UTC -7 — 8/23/2025 2:22 PM
2025-08-22; AD&D2ePbP Lords of Darkness Week Six; 1HR
Gammøn UTC -7 — 8/24/2025 12:17 PM
2024-08-24; DCE11 The Well of Reorx; 2HRs
divot (UTC -5) — 8/25/2025 11:56 PM
2025-08-25; Chronicles of Xandari: It Came From Below; 3 hours
Varvatos Vex (UTC -7) — 8/27/2025 12:03 PM
2025-08-26; Out of the Abyss (Session Sixty-Eight); 3 hours
Gammøn UTC -7 — 8/28/2025 9:10 PM
2025-08-28; DCE11 The Well of Reorx (Second Offering); 2HRs
Matrix (UTC-4/-5 in DST) — 8/28/2025 9:54 PM
2025-08-28; DDAL00-08  Layers Upon Layers PBP; 3 hours
Gammøn UTC -7 — 8/31/2025 1:00 PM
2025-08-29; AD&D2ePBP Lords of Darkness Week Seven; 1HR 
Gammøn UTC -7 — 8/31/2025 1:00 PM
2025-08-31; RV-DC-ROE-01 Roots of Evil (Vallaki Part One); 3HRs
Bloo37 (UTC -5/US Central) — 9/2/2025 12:13 AM
2025-09-1; Menace Under Otari (Part 3); 3 Hours
DigitalMatt (UTC-5/EST) — 9/4/2025 9:29 PM
2025-09-04; FR-DC-MELB-01-07 Secrets In the Deep; 2 hours
"""

# Splitting the data into lines
lines = data.strip().split("\n")

# Processed data
entries = []

for i in range(0, len(lines), 2):
    # Extract user name (first word of the first line)
    user_name = lines[i].split()[0]

    # Replace ø with o
    user_name = user_name.replace("ø", "o")

    # Extract event data from the second line
    try:
        event_data = lines[i + 1]
    except IndexError:
        print(f"Error at line {i + 1}: Missing event data. Previous line: {lines[i]}")
        exit(1)

    date_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", event_data)  # Match date format directly
    duration_match = re.search(r"(\d+(\.\d+)?)\s*(hours|HRs)", event_data, re.IGNORECASE)  # Match duration

    # Extract date and duration if found
    date = date_match.group(0) if date_match else ""
    duration = duration_match.group(1) if duration_match else ""

    # Extract and clean event name by removing date and duration patterns and trimming unnecessary characters
    event_name = re.sub(r"\b\d{4}-\d{2}-\d{2}\b|\s*\d+(\.\d+)?\s*(hours|HRs)", "", event_data).strip()
    event_name = re.sub(r"^[\s:;()]+|[\s:;()]+$", "", event_name)  # Clean the event name

    # Append if we have at least a date or an event name to avoid empty rows
    if date or event_name:
        entries.append([user_name, date, duration, event_name])

# Convert to DataFrame for easier handling
df = pd.DataFrame(entries, columns=["Name", "Date", "Duration", "Title"])

# Export the DataFrame to a CSV file
df.to_csv('cleaned_event_data.csv', index=False)
