import discord
import requests
import pyttsx3

#Configuração do arrombado:

TOKEN = "COLOQUE_SEU_NOVO_TOKEN_AQUI"

intents = discord.Intents.all()

client = discord.Client(intents=intents)

#Buscando a desgrama do fato:

def get_fact():
    url = "https://uselessfacts.jsph.pl/random.json"

    response = requests.get(url)

    print(response.json())

    if response.status_code == 200:
        data = response.json()
        return data["text"]

    return "I cant find a fact right now, sorry bro."

#Dando voz pra esse desgramado falar:

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

#Bot se conectando na desgrama do meu discord:

@client.event
async def on_ready():
    print(f"Sup, {client.user}")

#Hablando o desgrama:

@client.event
async def on_message(message):

    #Não ser esquizofrênico para não falar com si mesmo
    if message.author == client.user:
        return

    #Comando !bom dia
    if message.content.startswith("!hello"):
        await message.channel.send(
            "Hello negãum, what's eae?"
        )

    #Comando !fato
    elif message.content == "!fact":

        fact = get_fact()

        #Hacke seus dados e manda pro governo... mentira, ele manda o fato pro teu discord
        
        await message.channel.send(
            f"Here is your fact, bixãum: {fact}"
        )

        #Speak americano, aí depois toca a música braba... mentira denovo, ele só fala o fato.
        speak(fact)

# INICIAR BOT
client.run(TOKEN)