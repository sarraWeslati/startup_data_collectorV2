import json

from config import RAW_FILE, NORMALIZED_FILE



def get_content(article):


    # format Managers

    if "source_article" in article:

        return article.get(
            "source_article",
            {}
        ).get(
            "content",
            ""
        )


    # format Disrupt

    return article.get(
        "content",
        ""
    )



def get_source(article):


    if "source_article" in article:

        return article[
            "source_article"
        ].get(
            "url",
            ""
        )


    return article.get(
        "source",
        ""
    )




def normalize(article):


    result = {


        "title":
            article.get(
                "title",
                ""
            ),


        "summary":
            article.get(
                "summary",
                ""
            ),


        "content":
            get_content(article),


        "source":
            get_source(article),



        "date":
            article.get(
                "date",
                ""
            ),



        "country":
            article.get(
                "country",
                ""
            ),



        "category":
            article.get(
                "category",
                article.get(
                    "entity_type",
                    ""
                )
            ),



        "tags":
            article.get(
                "tags",
                []
            ),



        "entities":
            article.get(
                "entities",
                {

                "startups":[],
                "investors":[],
                "funds":[]

                }
            )

    }


    return result




with open(
    RAW_FILE,
    encoding="utf-8"
) as f:

    data=json.load(f)



normalized=[]


for article in data:

    normalized.append(
        normalize(article)
    )



with open(
    NORMALIZED_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        normalized,
        f,
        ensure_ascii=False,
        indent=2
    )



print(
    "Normalized:",
    len(normalized)
)