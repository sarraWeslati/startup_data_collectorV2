from retrieval.retriever import Retriever
from llm import generate_answer



retriever=Retriever()



print("\nChatbot ready ✅")
print("Tape exit pour quitter")




while True:


    question=input(
        "\nYou : "
    )



    if question.lower()=="exit":

        break




    docs=retriever.search(

        question,

        top_k=8

    )



    if not docs:

        print(
            "Aucune information trouvée."
        )

        continue




    context=""



    sources=[]



    for doc in docs:


        context += f"""

ARTICLE :

Titre :
{doc['title']}


Date :
{doc['date']}


Informations extraites :
{doc['metadata']}


Contenu :
{doc['text'][:2000]}



"""


        sources.append(
            doc["title"]
        )





    answer=generate_answer(

        question,

        context

    )



    print(
        "\nAssistant :\n"
    )


    print(answer)