import json

from config import FINAL_FILE, DOCUMENTS_FILE



with open(
    FINAL_FILE,
    encoding="utf-8"
) as f:

    news=json.load(f)



documents=[]



for i,item in enumerate(news):


    text=f"""
Title:
{item['title']}


Summary:
{item['summary']}


Content:
{item['content']}


Country:
{item['country']}


Category:
{item['category']}


Tags:
{', '.join(item['tags'])}

"""


    documents.append({

        "id":
            f"news_{i}",


        "text":
            text.strip(),


        "metadata":{

            "source":
                item["source"],


            "date":
                item["date"],


            "country":
                item["country"],


            "category":
                item["category"],


            "entities":
                item["entities"]

        }

    })




with open(
    DOCUMENTS_FILE,
    "w",
    encoding="utf-8"
) as f:


    json.dump(
        documents,
        f,
        ensure_ascii=False,
        indent=2
    )



print(
    "Documents:",
    len(documents)
)