import json
from pathlib import Path
from datetime import datetime



# ===============================
# CONFIG
# ===============================

INPUT_FILE = Path(
    "../data/clean_documents.json"
)

OUTPUT_FILE = Path(
    "../data/rag_documents.json"
)



# ===============================
# UTILITAIRES
# ===============================

def safe(value):

    if value is None:
        return ""

    if isinstance(value, list):
        return ", ".join(
            str(x)
            for x in value
            if x
        )

    if isinstance(value, dict):
        return ""

    return str(value)



def extract_list_names(items):

    result=[]

    if not isinstance(items,list):
        return result


    for item in items:

        if isinstance(item,dict):

            name=item.get("name")

            if name:
                result.append(name)


        elif isinstance(item,str):

            result.append(item)


    return result



# ===============================
# CREATION TEXTE RAG
# ===============================

def build_rag_text(doc):


    raw = doc.get(
        "raw_data",
        {}
    )


    parts=[]


    entity_type = (
        raw.get("entity_type")
        or doc.get("entity_type")
    )


    name = raw.get(
        "name",
        ""
    )


    description = raw.get(
        "description",
        ""
    )


    industry = raw.get(
        "industry",
        ""
    )


    country = raw.get(
        "country",
        ""
    )


    city = raw.get(
        "city",
        ""
    )


    if entity_type:
        parts.append(
            f"Entity type: {entity_type}"
        )


    if name:
        parts.append(
            f"Name: {name}"
        )


    if description:
        parts.append(
            f"Description: {description}"
        )


    if industry:
        parts.append(
            f"Industry: {industry}"
        )


    if country:
        parts.append(
            f"Country: {country}"
        )


    if city:
        parts.append(
            f"City: {city}"
        )



    # startup fields

    founders = extract_list_names(
        raw.get("founders",[])
    )

    if founders:

        parts.append(
            "Founders: "
            +
            ", ".join(founders)
        )



    products = extract_list_names(
        raw.get("products",[])
    )


    if products:

        parts.append(
            "Products: "
            +
            ", ".join(products)
        )



    # investor fields

    focus = raw.get(
        "investment_focus",
        []
    )


    if focus:

        parts.append(
            "Investment focus: "
            +
            ", ".join(focus)
        )



    stages = raw.get(
        "investment_stages",
        []
    )


    if stages:

        parts.append(
            "Investment stages: "
            +
            ", ".join(stages)
        )



    portfolio = extract_list_names(
        raw.get("portfolio_startups",[])
    )


    if portfolio:

        parts.append(
            "Portfolio startups: "
            +
            ", ".join(portfolio)
        )



    # financement

    funding = raw.get(
        "funding",
        {}
    )


    if isinstance(funding,dict):

        amount=funding.get(
            "total_raised"
        )

        currency=funding.get(
            "currency"
        )

        stage=funding.get(
            "stage"
        )


        if amount:

            parts.append(
                f"Funding: {amount} {currency}"
            )


        if stage:

            parts.append(
                f"Funding stage: {stage}"
            )



    # contenu article utile

    text = doc.get(
        "text",
        ""
    )


    if text:

        parts.append(
            "Additional information: "
            +
            text[:3000]
        )



    return "\n".join(parts)





# ===============================
# PREPARATION DOCUMENTS
# ===============================

def process():


    print("Loading documents...")


    with open(
        INPUT_FILE,
        encoding="utf-8"
    ) as f:

        documents=json.load(f)



    rag_docs=[]



    for index,doc in enumerate(documents):


        metadata = doc.get(
            "metadata",
            {}
        )


        rag_doc={


            "id":
                doc.get(
                    "id"
                ),


            "text":
                build_rag_text(
                    doc
                ),


            "metadata":{


                "entity_type":
                    metadata.get(
                        "entity_type"
                    ),


                "name":
                    metadata.get(
                        "name"
                    ),


                "country":
                    metadata.get(
                        "country"
                    ),


                "city":
                    metadata.get(
                        "city"
                    ),


                "industry":
                    metadata.get(
                        "industry"
                    ),


                "source":
                    metadata.get(
                        "source"
                    ),


                "prepared_at":
                    datetime.now().isoformat()

            }

        }



        rag_docs.append(
            rag_doc
        )



    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(
            rag_docs,
            f,
            ensure_ascii=False,
            indent=2
        )



    print(
        "RAG documents created:",
        len(rag_docs)
    )


    print(
        "Saved:",
        OUTPUT_FILE
    )




if __name__=="__main__":

    process()