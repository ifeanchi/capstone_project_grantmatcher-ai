from retrieval.semantic_search import semantic_search
from llm.chain import run_chain

results = semantic_search('health outreach', top_k=1)
print('Search result:', results)
if results:
    rationale = run_chain('We run community health workshops for preventive care.', results[0])
    print('\nRationale output:\n', rationale)
