import discord
from discord.ext import commands
import gspread
from google.oauth2 import service_account
import requests
import os

# Set up your Discord bot token and GitHub API token
DISCORD_BOT_TOKEN = 'your_discord_bot_token'
GITHUB_API_TOKEN = 'your_github_api_token'

# Google Sheets authentication and setup
def authenticate_google_sheets():
    google_credentials = service_account.Credentials.from_service_account_file('your_credentials.json')
    gc = gspread.authorize(google_credentials)
    return gc.open('your_google_sheet_name').sheet1

worksheet = authenticate_google_sheets()

# Additional helper function to find the user's row in the Google Sheet
def find_user_row(user_id):
    all_records = worksheet.get_all_records()
    row_number = 2
    for record in all_records:
        if record['Discord ID'] == user_id:
            return row_number
        row_number += 1
    return None

# Function to process user responses and match with relevant projects or tasks
def match_user_projects(user_id):
    all_records = worksheet.get_all_records()
    user_skills = []
    user_projects = []

    for record in all_records:
        if record['Discord ID'] == user_id:
            user_skills = record['Skills'].split(', ')
            break

    # Dummy projects/tasks data for demonstration
    projects_data = [
        {'name': 'Project 1', 'skills_required': ['Python', 'Django']},
        {'name': 'Project 2', 'skills_required': ['React', 'Node.js']},
        {'name': 'Project 3', 'skills_required': ['HTML', 'CSS', 'JavaScript']},
    ]

    for project in projects_data:
        if any(skill in user_skills for skill in project['skills_required']):
            user_projects.append(project['name'])

    return user_projects


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

def get_repository_details(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    response = requests.get(url, headers=headers)
    return response.json()

def create_issue(owner, repo, title, body=None, assignees=None, labels=None):
    url = f'https://api.github.com/repos/{owner}/{repo}/issues'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    data = {'title': title, 'body': body, 'assignees': assignees, 'labels': labels}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def search_repositories(query, sort=None, order=None):
    url = f'https://api.github.com/search/repositories?q={query}'
    if sort:
        url += f'&sort={sort}'
    if order:
        url += f'&order={order}'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    response = requests.get(url, headers=headers)
    return response.json()

def list_pull_requests(owner, repo, state='open'):
    url = f'https://api.github.com/repos/{owner}/{repo}/pulls?state={state}'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    response = requests.get(url, headers=headers)
    return response.json()

def create_pull_request(owner, repo, title, head, base, body=None):
    url = f'https://api.github.com/repos/{owner}/{repo}/pulls'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    data = {'title': title, 'head': head, 'base': base, 'body': body}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def get_team_details(team_id):
    url = f'https://api.github.com/teams/{team_id}'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    response = requests.get(url, headers=headers)
    return response.json()

def list_team_members(team_id):
    url = f'https://api.github.com/teams/{team_id}/members'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    response = requests.get(url, headers=headers)
    return response.json()

def create_webhook(owner, repo, events, config, active=True):
    url = f'https://api.github.com/repos/{owner}/{repo}/hooks'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    data = {'events': events, 'config': config, 'active': active}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def list_webhooks(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}/hooks'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    response = requests.get(url, headers=headers)
    return response.json()

# Function to create a new repository for a user
def create_repository(owner, repo_name, description=None, private=False):
    url = f'https://api.github.com/user/repos'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    data = {'name': repo_name, 'description': description, 'private': private}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Function to search for repositories with a specific topic or language
def search_repositories_with_topic_or_language(topic=None, language=None):
    query = ""
    if topic:
        query += f'topic:{topic}'
    if language:
        if query:
            query += f'+language:{language}'
        else:
            query += f'language:{language}'

    return search_repositories(query)

# Discord bot commands and events
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

@bot.command(name='find_projects')
async def find_projects(ctx):
    user_id = str(ctx.author.id)
    user_projects = match_user_projects(user_id)
    
    if user_projects:
        await ctx.send(f'{ctx.author.name}, here are some projects that match your skills: {", ".join(user_projects)}')
    else:
        await ctx.send(f'{ctx.author.name}, no matching projects found for your skills. Try updating your skills with the `!update_skills` command.')


@bot.command(name='list_repos')
async def list_repos(ctx, username):
    repos = list_repositories(username)
    if not repos:
        await ctx.send(f'No repositories found for user {username}.')
    else:
        repo_list = ', '.join([repo['name'] for repo in repos])
        await ctx.send(f'Repositories for user {username}: {repo_list}')

@bot.command(name='update_skills')
async def update_skills(ctx, *new_skills):
    user_id = str(ctx.author.id)
    user_row = find_user_row(user_id)

    if user_row:
        new_skills_str = ', '.join(new_skills)
        worksheet.update_cell(user_row, 3, new_skills_str)
        await ctx.send(f'{ctx.author.name}, your skills have been updated to: {new_skills_str}')
    else:
        await ctx.send(f'{ctx.author.name}, your Discord ID could not be found in the sheet. Please contact an administrator.')

def find_user_row(user_id):
    all_records = worksheet.get_all_records()
    row_number = 2  # Start from row 2 as row 1 contains column headers

    for record in all_records:
        if record['Discord ID'] == user_id:
            return row_number
        row_number += 1

    return None

bot.run(DISCORD_BOT_TOKEN)