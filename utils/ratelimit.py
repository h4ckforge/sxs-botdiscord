"""
Rate Limiting Utilities
Maneja cooldown diferenciado para usuarios normales vs admins
"""
from discord.ext import commands

def is_admin(ctx):
    """Check si el usuario tiene permisos de administrador"""
    if not ctx.guild:
        return False
    return ctx.author.guild_permissions.administrator

# Rate limits configurados
NORMAL_RATE = 3      # comandos
NORMAL_PER = 10      # segundos

ADMIN_RATE = 10      # comandos
ADMIN_PER = 60        # segundos

def get_cooldown(ctx):
    """Retorna el cooldown apropiado según el rol del usuario"""
    if is_admin(ctx):
        return commands.Cooldown(ADMIN_RATE, ADMIN_PER)
    return commands.Cooldown(NORMAL_RATE, NORMAL_PER)