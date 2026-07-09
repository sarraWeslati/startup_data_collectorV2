# main.py

import asyncio
import os
from dotenv import load_dotenv

from pipeline import run_pipeline


# -------------------------------------------------
# Chargement environnement
# -------------------------------------------------

load_dotenv()



# -------------------------------------------------
# Vérification NVIDIA KEY
# -------------------------------------------------

def check_environment():

    api_key = os.getenv(
        "NVIDIA_API_KEY"
    )


    if not api_key:

        raise Exception(
            """
❌ NVIDIA_API_KEY manquante.

Ajoute dans ton fichier .env :

NVIDIA_API_KEY=xxxxxxxxxxxxxxxx

"""
        )


    print(
        "✅ NVIDIA API key detected"
    )





# -------------------------------------------------
# Main
# -------------------------------------------------

async def main():


    print(
        """
====================================
🚀 WAMDA AFRICA NEWS PIPELINE
====================================
"""
    )


    check_environment()



    await run_pipeline()



    print(
        """
====================================
✅ PIPELINE FINISHED
📄 Output : news.json
====================================
"""
    )





if __name__ == "__main__":


    asyncio.run(
        main()
    )