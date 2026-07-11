from crawler import get_article_links

from pipeline import run_pipeline

from utils import save_json





if __name__=="__main__":


    print(
        "🚀 WAMDA NEWS PIPELINE"
    )



    urls=get_article_links()



    print(
        "TOTAL URLS:",
        len(urls)
    )



    news=run_pipeline(
        urls
    )



    save_json(
        news
    )



    print(
        "DONE:",
        len(news)
    )