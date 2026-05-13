"""
Validation Utilities
Sanitiza y valida inputs de usuario
"""
import re

def sanitize_text(text: str, max_length: int = 2000) -> str:
    """
    Sanitiza texto para evitar problemas de formato.
    - Limita longitud máxima
    - Remueve caracteres de control problemáticos

    Args:
        text: Texto a sanitizar
        max_length: Longitud máxima permitida

    Returns:
        Texto sanitizado
    """
    if not text:
        return ""

    # Remover caracteres de control (excepto saltos de línea válidos)
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)

    # Limitar longitud
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()

def sanitize_mention(mention: str) -> str:
    """
    Valida que una mención de usuario/rol sea segura.
    Solo permite formatos válidos de Discord: <@user_id>, <@&role_id>, <#channel_id>
    """
    if not mention:
        return ""

    # Solo permitir mentions válidas de Discord
    pattern = r'^<@!?\d+>$|^<@&\d+>$|^<#\d+>$'
    if re.match(pattern, mention):
        return mention

    return ""  # Invalid mention, return empty

def validate_member_id(member_id: str) -> bool:
    """
    Valida que un ID de miembro sea numérico y válido para Discord.
    Discord IDs son enteros de hasta 20 dígitos.
    """
    if not member_id:
        return False

    # Remover mention format if present
    member_id = re.sub(r'[<>@!]', '', member_id)

    # Verificar que sea numérico y длиной razonable
    return member_id.isdigit() and len(member_id) <= 20