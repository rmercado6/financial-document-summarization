CHUNK_SIZE = {
    'gpt': 100000,
    'llama': 8000,
    'mistral': 32000,
}

CHUNK_OVERLAP = {
    'gpt': 5000,
    'llama': 500,
    'mistral': 3200,
}

MODELS = ['gpt', 'llama', 'mistral']
DEFAULT_MODEL = 'gpt'

PIPELINES = ['refine', 'mapreduce']
DEFAULT_PIPELINE = 'refine'
