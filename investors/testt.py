import json

with open("investors.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Nombre d'investisseurs :", len(data["investors"]))