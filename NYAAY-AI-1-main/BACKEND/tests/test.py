from duckduckgo_search import DDGS

with DDGS() as ddgs:
    results = ddgs.text('site:indiankanoon.org "Semiconductor Integrated Circuits Layout-Design Act"', max_results=3)
    for r in results:
        print(r['href'])
