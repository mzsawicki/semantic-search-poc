UNIVERSAL_SENTENCE_ENCODER_MAPPING = {
    'mappings': {
        'properties': {
            'title': {'type': 'text', 'index': True},
            'summary': {'type': 'text', 'index': True},
            'content': {'type': 'text', 'index': False},
            'title_embed': {'type': 'dense_vector', 'dims': 512, 'index': True, 'similarity': 'cosine'},
            'summary_embed': {'type': 'dense_vector', 'dims': 512, 'index': True, 'similarity': 'cosine'},
            'content_embed': {'type': 'dense_vector', 'dims': 512, 'index': True, 'similarity': 'cosine'}
        }
    }
}
