import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
import subprocess
import shlex

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv(dotenv_path='~/Workspace/SystemControlBot/.env')

from services.pdf_service import PDFService
from services.voice_service import VoiceService
from services.google_service import GoogleWorkspaceService
from services.image_service import ImageAnalysisService
from services.search_service import SearchService
from commands.quiz_command import QuizCommand

# Initialize services
pdf_service = PDFService()
voice_service = VoiceService()
google_service = GoogleWorkspaceService()
image_service = ImageAnalysisService()
search_service = SearchService()
quiz_command = QuizCommand()

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix='!', 
    intents=intents,
    description="Abrar AI: A multimodal system-control bot capable of document generation, voice synthesis, image analysis, and shell command execution."
)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}')
    logging.info("Abrar AI is online and ready for multimodal operations: Documents, Audio, Image Analysis, and System Control.")
from services.shell_service import CloudShellService

# Initialize services
shell_service = CloudShellService()

@bot.command()
async def run(ctx, filename: str):
    """Executes a local script file with automatic interpreter detection."""
    if not filename.startswith('~/'):
        await ctx.send("Access denied: File must be in the home directory.")
        return
    
    if not os.path.exists(filename):
        await ctx.send("File not found.")
        return

    # Language mapping for execution
    executors = {
        '.py': ['python3'],
        '.js': ['node'],
        '.go': ['go', 'run'],
        '.rb': ['ruby'],
        '.sh': ['bash'],
        '.cpp': ['g++', '-o', 'temp_exec', filename, '&&', './temp_exec'],
        '.c': ['gcc', '-o', 'temp_exec', filename, '&&', './temp_exec']
    }

    ext = os.path.splitext(filename)[1]
    if ext not in executors:
        await ctx.send(f"Unsupported file type: {ext}. Add an entry to the executor map.")
        return

    cmd_base = executors[ext]
    # For compiled languages, we just use the pre-defined list
    if ext in ['.cpp', '.c']:
        command = cmd_base
        shell_exec = True
    else:
        command = cmd_base + [filename]
        shell_exec = False

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15, shell=shell_exec)
        output = result.stdout if result.stdout else result.stderr
        if not output: output = "Script executed successfully with no output."
        if len(output) > 1900: output = output[:1900] + "\n... (truncated)"
        await ctx.send(f"Result:\n```\n{output}\n```")
    except Exception as e:
        await ctx.send(f"Execution error: {str(e)}")

async def read_file(ctx, file_path: str):
    """Reads a file from the local system (server-scoped access)"""
    if not file_path.startswith('~/'):
        await ctx.send("Access denied: Invalid file path.")
        return
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        if len(content) > 1900: content = content[:1900] + "\n... (truncated)"
        await ctx.send(f"Content of `{file_path}`:\n```\n{content}\n```")
    except Exception as e:
        await ctx.send(f"Error reading file: {str(e)}")

@bot.command()
async def analyze(ctx):
    """Analyzes an image attachment using LLaVA"""
    if not ctx.message.attachments:
        await ctx.send("Please attach an image to analyze.")
        return
    attachment = ctx.message.attachments[0]
    file_path = f"~/Workspace/SystemControlBot/data/{attachment.filename}"
    await attachment.save(file_path)
    analysis = image_service.analyze_image(file_path)
    await ctx.send(f"Image Analysis:\n{analysis}")

@bot.command()
async def search(ctx, *, query: str):
    """Searches using Google CSE"""
    results = search_service.search(query)
    await ctx.send(f"Search Results:\n{results}")

@bot.command()
async def quiz(ctx):
    """Starts an interactive quiz."""
    quiz_command.execute()
    await ctx.send("Quiz finished! Check logs for details.")

@bot.command()
async def create_doc(ctx, *, title: str):
    doc_id = google_service.create_doc(title)
    await ctx.send(f"Created Doc: https://docs.google.com/document/d/{doc_id}")

@bot.command()
async def create_sheet(ctx, *, title: str):
    sheet_id = google_service.create_sheet(title)
    await ctx.send(f"Created Sheet: https://docs.google.com/spreadsheets/d/{sheet_id}")

@bot.command()
async def create_slide(ctx, *, title: str):
    slide_id = google_service.create_slide(title)
    await ctx.send(f"Created Slide: https://docs.google.com/presentation/d/{slide_id}")

@bot.command()
async def create_pdf(ctx, *, text: str):
    filename = pdf_service.create_pdf(text)
    await ctx.send(file=discord.File(filename))

@bot.command()
async def join(ctx):
    """Joins the user's voice channel."""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Joined {channel.name}")
    else:
        await ctx.send("You are not in a voice channel.")

@bot.command()
async def leave(ctx):
    """Leaves the voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from voice channel.")
    else:
        await ctx.send("I am not in a voice channel.")

@bot.command()
async def speak(ctx, *, text: str):
    """Generates speech and plays it in the voice channel."""
    if not ctx.voice_client:
        await ctx.send("I am not in a voice channel. Please use `!join` first.")
        return

    filename = voice_service.generate_audio(text)
    
    # Play the generated audio file
    source = discord.FFmpegPCMAudio(filename)
    ctx.voice_client.play(source)
    await ctx.send("Speaking...")

if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
