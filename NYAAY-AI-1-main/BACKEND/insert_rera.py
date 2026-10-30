
import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.knowledge.vector_store import vector_store
from app.knowledge.embeddings import embedding_service
from app.knowledge.bm25_manager import bm25_manager

text = 'Real Estate (Regulation and Development) Act, 2016 (RERA) Section 18: Return of amount and compensation. If the promoter fails to complete or is unable to give possession of an apartment, plot or building, in accordance with the terms of the agreement for sale or, as the case may be, duly completed by the date specified therein, he shall be liable on demand to the allottees, in case the allottee wishes to withdraw from the project, without prejudice to any other remedy available, to return the amount received by him in respect of that apartment, plot, building, as the case may be, with interest at such rate as may be prescribed in this behalf including compensation in the manner as provided under this Act.'

meta = {
    'act_name': 'Real Estate (Regulation and Development) Act, 2016',
    'section': '18',
    'document_type': 'statute',
    'legal_domain': 'Consumer Law', # or 'Property & Real Estate'
    'source_name': 'Real Estate (Regulation and Development) Act, 2016'
}

emb = embedding_service.embed_query(text)
vector_store.collection.add(
    ids=['rera_mock_1'],
    documents=[text],
    metadatas=[meta],
    embeddings=[emb]
)
print('Inserted RERA chunk.')
bm25_manager.rebuild_index('global')
print('BM25 index rebuilt.')

