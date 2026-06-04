import requests

# TODO: Replace with your GitHub Personal Access Token (PAT)
TOKEN = ""
REPO = "ocxers/stock-picks-daily"

headers = {"Authorization": f"token {TOKEN}"}

# Enable GitHub Pages
payload = {
    "source": {
        "branch": "main",
        "path": "/"
    }
}

resp = requests.post(
    f"https://api.github.com/repos/{REPO}/pages",
    json=payload,
    headers=headers
)

if resp.status_code == 201:
    print("GitHub Pages enabled successfully.")
elif resp.status_code == 403:
    # Might be already enabled or permission issue
    check = requests.get(f"https://api.github.com/repos/{REPO}/pages", headers=headers)
    if check.status_code == 200:
        pages_data = check.json()
        print(f"GitHub Pages is active at: {pages_data['html_url']}")
    else:
        print(f"Pages status unknown: {check.text}")
else:
    print(f"Failed to enable pages: {resp.status_code} - {resp.text}")
