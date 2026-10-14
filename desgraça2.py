import discord
from discord.ext import commands
import aiohttp
import random
import os
from datetime import datetime

# ==================== CONFIGURAÇÃO ====================
TOKEN = os.getenv("DISCORD_TOKEN") or "COLOQUE_SEU_TOKEN_AQUI"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # necessário para userinfo completo

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None  # vamos fazer nosso próprio help
)

# ==================== FUNÇÕES AUXILIARES ====================
async def fetch_json(url: str, headers: dict = None):
    """Faz uma requisição HTTP assíncrona e retorna o JSON."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers or {}) as response:
            if response.status == 200:
                return await response.json()
            return None


def create_embed(title: str, description: str = None, color: int = 0x5865F2):
    """Cria um embed padrão bonito."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="Bot do desgrama 🔥")
    return embed


# ==================== EVENTOS ====================
@bot.event
async def on_ready():
    print(f"✅ Logado como {bot.user} (ID: {bot.user.id})")
    print(f"📡 Conectado em {len(bot.guilds)} servidor(es)")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="!help | fatos inúteis"
        )
    )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Comando não encontrado. Use `!help` pra ver a lista.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Faltou um argumento. Use `!help` pra ver como usar.")
    else:
        await ctx.send(f"❌ Ocorreu um erro: `{error}`")
        raise error  # pra aparecer no console também


# ==================== COMANDOS BÁSICOS ====================
@bot.command(name="hello", aliases=["oi", "eae", "bomdia"])
async def hello(ctx):
    """Saudação descontraída."""
    greetings = [
        f"Eae {ctx.author.mention}, tudo bem por aí?",
        f"Fala {ctx.author.mention}! Beleza?",
        f"Oi {ctx.author.mention}, chegou o rei 👑",
        f"Salve {ctx.author.mention}! Bora quebrar o pau?",
    ]
    await ctx.send(random.choice(greetings))


@bot.command(name="ping")
async def ping(ctx):
    """Mostra a latência do bot."""
    latency = round(bot.latency * 1000)
    embed = create_embed(
        title="🏓 Pong!",
        description=f"Latência: **{latency}ms**",
        color=0x57F287 if latency < 100 else 0xFEE75C if latency < 200 else 0xED4245
    )
    await ctx.send(embed=embed)


@bot.command(name="help", aliases=["ajuda", "comandos"])
async def help_command(ctx):
    """Mostra todos os comandos disponíveis."""
    embed = create_embed(
        title="📜 Lista de Comandos",
        description="Prefixo: `!`\n\n"
                    "**Diversão**\n"
                    "`!hello` / `!oi` — Saudação\n"
                    "`!fact` — Fato inútil aleatório\n"
                    "`!joke` — Piada aleatória\n"
                    "`!advice` — Conselho aleatório\n"
                    "`!coinflip` — Cara ou coroa\n"
                    "`!dice [lados]` — Rola um dado (padrão 6)\n\n"
                    "**Animais**\n"
                    "`!dog` — Foto de cachorro\n"
                    "`!cat` — Foto de gato\n\n"
                    "**Utilidade**\n"
                    "`!ping` — Latência do bot\n"
                    "`!avatar [@user]` — Avatar de alguém\n"
                    "`!userinfo [@user]` — Info de um usuário\n"
                    "`!serverinfo` — Info do servidor",
        color=0xEB459E
    )
    await ctx.send(embed=embed)


# ==================== COMANDOS DE DIVERSÃO ====================
@bot.command(name="fact", aliases=["fato"])
async def fact(ctx):
    """Pega um fato inútil aleatório."""
    data = await fetch_json("https://uselessfacts.jsph.pl/api/v2/facts/random?language=en")
    
    if data and "text" in data:
        embed = create_embed(
            title="🧠 Fato Inútil",
            description=data["text"],
            color=0x5865F2
        )
        if "source" in data:
            embed.set_footer(text=f"Fonte: {data.get('source', 'desconhecida')}")
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Não consegui achar um fato agora, tenta de novo.")


@bot.command(name="joke", aliases=["piada"])
async def joke(ctx):
    """Conta uma piada aleatória."""
    data = await fetch_json("https://official-joke-api.appspot.com/random_joke")
    
    if data:
        embed = create_embed(
            title="😂 Piada",
            description=f"**{data['setup']}**\n\n||{data['punchline']}||",
            color=0xFEE75C
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ As piadas acabaram... ou a API caiu.")


@bot.command(name="advice", aliases=["conselho"])
async def advice(ctx):
    """Dá um conselho aleatório."""
    data = await fetch_json("https://api.adviceslip.com/advice")
    
    if data and "slip" in data:
        embed = create_embed(
            title="💡 Conselho do dia",
            description=data["slip"]["advice"],
            color=0x57F287
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Sem conselhos por agora.")


@bot.command(name="coinflip", aliases=["moeda", "caraoucoroa"])
async def coinflip(ctx):
    """Cara ou coroa."""
    result = random.choice(["🟢 **CARA**", "🔴 **COROA**"])
    embed = create_embed(
        title="🪙 Cara ou Coroa",
        description=f"Resultado: {result}",
        color=0xFEE75C
    )
    await ctx.send(embed=embed)


@bot.command(name="dice", aliases=["dado", "roll"])
async def dice(ctx, sides: int = 6):
    """Rola um dado com N lados (padrão 6)."""
    if sides < 2 or sides > 1000:
        return await ctx.send("❌ O dado precisa ter entre 2 e 1000 lados.")
    
    result = random.randint(1, sides)
    embed = create_embed(
        title="🎲 Rolagem de Dado",
        description=f"Você rolou um **d{sides}** e tirou: **{result}**",
        color=0xEB459E
    )
    await ctx.send(embed=embed)


# ==================== COMANDOS DE ANIMAIS ====================
@bot.command(name="dog", aliases=["cachorro", "doggo"])
async def dog(ctx):
    """Envia uma foto aleatória de cachorro."""
    data = await fetch_json("https://dog.ceo/api/breeds/image/random")
    
    if data and data.get("status") == "success":
        embed = create_embed(title="🐶 Au au!", color=0x57F287)
        embed.set_image(url=data["message"])
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Os doguinhos estão ocupados.")


@bot.command(name="cat", aliases=["gato", "gatinho"])
async def cat(ctx):
    """Envia uma foto aleatória de gato."""
    data = await fetch_json("https://api.thecatapi.com/v1/images/search")
    
    if data and len(data) > 0:
        embed = create_embed(title="🐱 Miau!", color=0xEB459E)
        embed.set_image(url=data[0]["url"])
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Os gatos estão dormindo.")


# ==================== COMANDOS DE UTILIDADE ====================
@bot.command(name="avatar", aliases=["av"])
async def avatar(ctx, member: discord.Member = None):
    """Mostra o avatar de um usuário."""
    member = member or ctx.author
    embed = create_embed(
        title=f"Avatar de {member.display_name}",
        color=member.color if member.color.value else 0x5865F2
    )
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="userinfo", aliases=["user", "whois"])
async def userinfo(ctx, member: discord.Member = None):
    """Mostra informações de um usuário."""
    member = member or ctx.author
    
    roles = [role.mention for role in member.roles[1:]]  # remove @everyone
    roles_text = ", ".join(roles) if roles else "Nenhum"
    
    embed = create_embed(
        title=f"👤 {member}",
        color=member.color if member.color.value else 0x5865F2
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Apelido", value=member.display_name, inline=True)
    embed.add_field(name="Bot?", value="Sim" if member.bot else "Não", inline=True)
    embed.add_field(
        name="Entrou no servidor",
        value=discord.utils.format_dt(member.joined_at, "R") if member.joined_at else "?",
        inline=True
    )
    embed.add_field(
        name="Conta criada",
        value=discord.utils.format_dt(member.created_at, "R"),
        inline=True
    )
    embed.add_field(name=f"Cargos ({len(roles)})", value=roles_text[:1024], inline=False)
    
    await ctx.send(embed=embed)


@bot.command(name="serverinfo", aliases=["server", "guild"])
async def serverinfo(ctx):
    """Mostra informações do servidor."""
    guild = ctx.guild
    
    embed = create_embed(
        title=f"📊 {guild.name}",
        color=0x5865F2
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.add_field(name="Dono", value=guild.owner.mention if guild.owner else "?", inline=True)
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Criado em", value=discord.utils.format_dt(guild.created_at, "R"), inline=True)
    embed.add_field(name="Membros", value=guild.member_count, inline=True)
    embed.add_field(name="Canais", value=len(guild.channels), inline=True)
    embed.add_field(name="Cargos", value=len(guild.roles), inline=True)
    
    await ctx.send(embed=embed)


# ==================== INICIAR O BOT ====================
if __name__ == "__main__":
    if not TOKEN or TOKEN == "COLOQUE_SEU_TOKEN_AQUI":
        print("❌ ERRO: Coloque o token do bot!")
        print("   Opção 1: Edite a variável TOKEN no código")
        print("   Opção 2: Defina a variável de ambiente DISCORD_TOKEN")
    else:
        bot.run(TOKEN)
