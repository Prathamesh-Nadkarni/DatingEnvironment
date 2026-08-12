import os

base = "/Users/pratham/Desktop/Sandbox/Dating App/frontend/src/"
files = ["App.svelte", "Dashboard.svelte", "Admin.svelte"]

for f in files:
    path = os.path.join(base, f)
    with open(path, "r") as file:
        content = file.read()
    content = content.replace("#fbbf24", "var(--accent)")
    content = content.replace("rgba(251, 191, 36, 0.1)", "var(--accent-bg)")
    content = content.replace("rgba(251, 191, 36, 0.4)", "var(--accent-border)")
    content = content.replace("rgba(251, 191, 36", "var(--accent-bg-raw")
    with open(path, "w") as file:
        file.write(content)
print("Replaced hardcoded colors!")
