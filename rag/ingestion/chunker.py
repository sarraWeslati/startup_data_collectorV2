import json

from langchain_text_splitters import RecursiveCharacterTextSplitter


INPUT = "../data/documents.json"
OUTPUT = "../data/chunks.json"



def main():

    with open(
        INPUT,
        encoding="utf-8"
    ) as f:

        documents = json.load(f)



    splitter = RecursiveCharacterTextSplitter(

        chunk_size=1500,

        chunk_overlap=300,

        separators=[
            "\n\n",
            "\n",
            ". ",
            " "
        ]

    )



    chunks = []



    for doc in documents:


        texts = splitter.split_text(
            doc["text"]
        )



        for i, text in enumerate(texts):


            metadata = doc.get(
                "metadata",
                {}
            )


            enriched_text = f"""
Titre:
{metadata.get('title','')}


Date:
{metadata.get('date','')}


Catégorie:
{metadata.get('category','')}


Secteurs:
{metadata.get('sectors','')}


Source:
{metadata.get('source_url','')}


Contenu:
{text}
"""



            chunks.append(

                {

                    "chunk_id":
                    f"{doc['id']}_{i}",


                    "text":
                    enriched_text.strip(),


                    "metadata":
                    {

                        **metadata,


                        "chunk_number":
                        i

                    }

                }

            )



    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(

            chunks,

            f,

            ensure_ascii=False,

            indent=2

        )



    print(
        len(chunks),
        "chunks created"
    )



if __name__=="__main__":
    main()