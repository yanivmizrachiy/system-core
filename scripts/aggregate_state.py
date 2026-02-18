import json, os, glob, datetime

def safe_load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return None

timestamp = datetime.datetime.utcnow().isoformat()

# latest governance raw
gov_dirs = sorted(glob.glob("STATE/governance-v4/*"), reverse=True)
gov = None
if gov_dirs:
    gov = safe_load(os.path.join(gov_dirs[0], "raw.json"))

# pdf-system latest
pdf_path = os.path.expanduser("../pdf-system/STATE/latest/latest.json")
pdf = safe_load(pdf_path)

health = 0
if gov: health += 40
if pdf and pdf.get("status") == "PASS": health += 30
cloud_verified = False

unified = {
    "timestamp": timestamp,
    "system_core": gov if gov else "NO_DATA",
    "pdf_system": pdf if pdf else "NO_DATA",
    "cloud_verified": cloud_verified,
    "health_score": health
}

with open("STATE/unified/latest.json","w") as f:
    json.dump(unified, f, indent=2)

with open("docs/data/unified.json","w") as f:
    json.dump(unified, f, indent=2)

print("Unified state generated.")
