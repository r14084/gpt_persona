import os
import pandas as pd
import re
from openai import OpenAI



# === SET YOUR API KEY ===
client = OpenAI(api_key="your-API")  # Replace with your actual key

# === INTERACTIVE INPUTS ===
csv_path_or_url = input("🔗 Enter Google Sheet CSV link or local .csv file path: ").strip()
persona_name = input("👤 Enter persona name (matches markdown filename): ").strip()
script_word_count = int(input("✍️ Enter desired word count (e.g., 2500): ").strip())
language = input("🌐 Enter script language (eng for English, thai for Thai): ").strip().lower()

# === LANGUAGE PROMPT TAG ===
if language == "thai":
    lang_instruction = "Write the script in Thai language."
elif language == "eng":
    lang_instruction = "Write the script in English language."
else:
    raise ValueError("Unsupported language. Please enter 'thai' or 'eng'.")

# === LOAD TOPICS ===
if csv_path_or_url.startswith("http"):
    df = pd.read_csv(csv_path_or_url,header=0)
else:
    df = pd.read_csv(csv_path_or_url)

# === LOAD PERSONA FILE ===
persona_file = f"{persona_name}.md"
if not os.path.exists(persona_file):
    raise FileNotFoundError(f"❌ Persona file '{persona_file}' not found.")
with open(persona_file, 'r', encoding='utf-8') as f:
    persona_content = f.read()

# === CREATE OUTPUT FOLDER ===
output_dir = "generated_scripts"
os.makedirs(output_dir, exist_ok=True)

# === GENERATE SCRIPTS ===
for idx, row in df.iterrows():
    topic = str(row["Topic"]).strip()
    print(f"🚧 Generating script for: {topic}")

    prompt = f"""
You are to write a YouTube script based on the following persona:

{persona_content}

Topic: {topic}

Please write a YouTube script of approximately {script_word_count} words that reflects the tone and personality of the persona described above.
{lang_instruction}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # use gpt-4 if you have access
        messages=[
            {"role": "system", "content": "You are a helpful content writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    script = response.choices[0].message.content
    safe_topic = re.sub(r'[\\/*?:"<>|]', "", topic[:50].replace(" ", "_"))
    file_path = os.path.join(output_dir, f"script_{idx+1:02d}_{safe_topic}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# YouTube Script for: {topic}\n\n{script}")

print(f"\n✅ Done! All scripts saved in the '{output_dir}' folder.")
