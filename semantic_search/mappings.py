UNIVERSAL_SENTENCE_ENCODER_MAPPING = {
    'mappings': {
        'properties': {
            'title': {'type': 'text'},
            'summary': {'type': 'text'},
            'content': {'type': 'text'},
            'title_embed': {'type': 'dense_vector', 'dims': 512, 'index': True, 'similarity': 'cosine'},
            'summary_embed': {'type': 'dense_vector', 'dims': 512, 'index': True, 'similarity': 'cosine'},
            'content_embed': {'type': 'dense_vector', 'dims': 512, 'index': True, 'similarity': 'cosine'}
        }
    }
}
