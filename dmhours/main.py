import re
import pandas as pd

# Reinitialize the raw data
data = """
sterling UTC-6 — 9/8/2025 12:48 AM
Like a Bard Outta Hell 2025-09-07 3.5 hrs
Gammøn UTC -7 — 9/8/2025 2:23 PM
2025-09-05; AD&D2ePbP Lords of Darkness Wk08; 1HR
Varvatos Vex (UTC -7) — 9/10/2025 12:01 PM
2025-09-02; Out of the Abyss (Session Sixty-Nine); 3 hours
Varvatos Vex (UTC -7) — 9/10/2025 12:01 PM
2025-09-09; Out of the Abyss (Session Seventy); 3 hours
Varvatos Vex (UTC -7) — 9/10/2025 12:01 PM
2025-09-01; DDAL-09-08 (In the Garden of Evil); 5 hours
DigitalMatt (UTC-5/EST) — 9/11/2025 8:52 PM
2025-09-11; FR-DC-MELB-01-07 Secrets In the Deep; 2 hours
sterling UTC-6 — 9/14/2025 12:10 AM
2025-09-13 Ad Astra: The Highest Bidder 3hrs
divot (UTC -5) — 9/15/2025 11:58 PM
2025-09-15 Chronicles of Xandari: Tussle at Tide Pool Tavern part 1; 2 hours
Varvatos Vex (UTC -7) — 9/17/2025 1:42 PM
2025-09-16; Out of the Abyss (Session Seventy-One); 3 hours
Gammøn UTC -7 — 9/17/2025 1:43 PM
2025-09-12; AD&D2ePbP Lords of Darkness Wk09; 1HR
sterling UTC-6 — 9/20/2025 10:46 AM
2025-09-19 Ad Astra: The Highest Bidder Part 2, 3 hours
Gammøn UTC -7 — 9/20/2025 5:31 PM
2025-09-19; AD$D2ePbP Lords of Darkness Wk10; 1HR
Gammøn UTC -7 — 9/21/2025 12:57 PM
2025-09-21; Roots of Evil Part 2; 3HRs
divot (UTC -5) — 9/22/2025 10:13 PM
2025-09-22; Chronicles of Darkness: Tussle at Tide Pool Tavern part 2; 1 hour
Varvatos Vex (UTC -7) — 9/25/2025 9:13 PM
2025-09-23; Out of the Abyss (Session Seventy-Two); 3 hours
Gammøn UTC -7 — 9/27/2025 5:26 PM
2025-09-26; Lords of Darkness WK11: 1HR
Gammøn UTC -7 — 9/28/2025 12:24 PM
2025-09-28; DCE12-The Fall of Tarsis; 2HRs
DigitalMatt (UTC-5/EST) — 10/2/2025 10:47 PM
2025-10-02; DDHC-DD-01 Death at Sunset; 3 hours
Gammøn UTC -7 — 10/6/2025 1:14 AM
2025-10-05; Roots of Evil Part Three; 3.5HRs
sterling UTC-6 — 10/7/2025 9:48 AM
2025-10-06 Happy Jack's Funhouse Part 1, 3 hrs
Matrix (UTC-4/-5 in DST) — Yesterday at 11:18 PM
2025-10-04 and 20205-10-10   DDAL05-14  Reeducation; 5 hours
Gammøn UTC -7 — Yesterday at 11:53 PM
2025-10-09; DCE12 Fall of Tarsis; 2HRs
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
