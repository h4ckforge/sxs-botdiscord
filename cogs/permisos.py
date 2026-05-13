import discord
from discord.ext import commands
 
class Permisos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
 
    @commands.command(name='permisos')
    @commands.has_permissions(administrator=True)
    #async def check_permisos(self, ctx, miembro: discord.Member, canal: discord.TextChannel = None):
    async def check_permisos(self, ctx, miembro: discord.Member, canal: discord.abc.GuildChannel = None):
        """
        Desc: Muestra los permisos efectivos de un usuario en un canal.
        Uso: !permisos @usuario #canal
        Si no se especifica canal, usa el canal actual.
        """
        canal = canal or ctx.channel
 
        permisos = canal.permissions_for(miembro)
        roles = [r.name for r in miembro.roles if r.name != "@everyone"]
 
        permisos_relevantes = {
            "Ver canal": permisos.view_channel,
            "Enviar mensajes": permisos.send_messages,
            "Leer historial": permisos.read_message_history,
            "Adjuntar archivos": permisos.attach_files,
            "Añadir reacciones": permisos.add_reactions,
            "Conectarse a voz": permisos.connect,
            "Hablar en voz": permisos.speak,
            "Usar comandos de apps": permisos.use_application_commands,
            "Mencionar @everyone": permisos.mention_everyone,
            "Gestionar mensajes": permisos.manage_messages,
            "Gestionar canal": permisos.manage_channels,
            "Gestionar roles": permisos.manage_roles,
        }
 
        lineas_permisos = []
        for nombre, valor in permisos_relevantes.items():
            emoji = "✅" if valor else "❌"
            lineas_permisos.append(f"{emoji} {nombre}")
 
        categoria = canal.category.name if canal.category else "Sin categoría"
        roles_str = ", ".join(roles) if roles else "Sin roles"
 
        respuesta = (
            f"```\n"
            f"DIAGNOSTICO DE PERMISOS\n"
            f"Usuario  : {miembro.display_name}\n"
            f"Canal    : #{canal.name}\n"
            f"Categoria: {categoria}\n"
            f"Roles    : {roles_str}\n"
            f"\nPermisos efectivos:\n"
            + "\n".join(lineas_permisos) +
            f"\n```"
        )
 
        await ctx.send(respuesta)
 
async def setup(bot):
    await bot.add_cog(Permisos(bot))