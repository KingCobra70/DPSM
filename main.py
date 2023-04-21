import discord
from discord.ext import commands
import gspread
from google.oauth2 import service_account
import requests
import os

# Set up your Discord bot token and GitHub API token
DISCORD_BOT_TOKEN = 'your_discord_bot_token'
GITHUB_API_TOKEN = 'your_github_api_token'


def authenticate_google_sheets():
    # Set up the Google Sheets API credentials
    google_credentials = service_account.Credentials.from_service_account_file('your_credentials.json')

    # Authenticate with Google Sheets
    gc = gspread.authorize(google_credentials)

    # Open the Google Sheet and return the worksheet
    return gc.open('your_google_sheet_name').sheet1

worksheet = authenticate_google_sheets()

def get_github_user(username):
    url = f'https://api.github.com/users/{username}'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    response = requests.get(url, headers=headers)
    return response.json()

def list_repositories(user):
    url = f'https://api.github.com/users/{user}/repos'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    response = requests.get(url, headers=headers)
    return response.json()

# Add more GitHub API functions as needed


bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='github_user')
async def github_user(ctx, username):
    user_data = get_github_user(username)
    if 'message' in user_data and user_data['message'] == 'Not Found':
        await ctx.send(f'GitHub user {username} not found.')
    else:
        await ctx.send(f'GitHub user {username} found with {user_data["public_repos"]} public repositories.')

@bot.command(name='list_repos')
async def list_repos(ctx, username):
    repos = list_repositories(username)
    if not repos:
        await ctx.send(f'No repositories found for user {username}.')
    else:
        repo_list = ', '.join([repo['name'] for repo in repos])
        await ctx.send(f'Repositories for user {username}: {repo_list}')

# Add more Discord bot commands and events as needed

bot.run(DISCORD_BOT_TOKEN)


