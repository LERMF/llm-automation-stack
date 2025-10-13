# Rotação automática baseada em quotas
providers = {
    'ollama': {'quota': float('inf'), 'local': True},
    'groq': {'quota': 14400, 'used': 0},
    'replicate': {'quota': 5000, 'used': 0}
}

def get_available_provider():
    for name, info in providers.items():
        if info['used'] < info['quota']:
            return name
    return 'ollama'  # fallback local
