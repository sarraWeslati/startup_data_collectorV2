from pdf_llm_extractor import run_pdf_llm_extraction
import json


def main():

    startups = run_pdf_llm_extraction()

    print(f"\n✅ {len(startups)} startups extraites\n")

    for i, startup in enumerate(startups, start=1):
     
     print(f"STARTUP {i}")
     print("=" * 80)

     print("Nom :", startup.get("nom"))
     print("Secteur :", startup.get("secteur"))
     print("Website :", startup.get("site_web"))
     print("Description :", startup.get("description", "")[:300])
     print()

    with open("pdf_output.json", "w", encoding="utf-8") as f:
        json.dump(startups, f, ensure_ascii=False, indent=2)

    print("💾 Résultat sauvegardé dans pdf_output.json")


if __name__ == "__main__":
    main()