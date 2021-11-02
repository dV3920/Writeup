import requests
key = "XXX"
response = requests.get("https://discordapp.com/api/v6/guilds/879999382718644234/channels",
        headers = {"authorization" : key})

print(response.content)