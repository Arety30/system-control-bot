# SystemControlBot

SystemControlBot is a Discord bot in Python that exposes a handful of "do something on my machine or in my accounts" commands behind a `!` prefix: run a script file from the home directory with the right interpreter, describe an attached image with a local Ollama model, search the web through Google Custom Search, create an empty Google Doc / Sheet / Slides deck, render a short PDF, and join a voice channel to read text aloud with ElevenLabs speech. It is organised as a thin command layer (`bot.py`, `commands/`) over small single-purpose service classes (`services/`), so each capability can be swapped or tested on its own.

## Where it is used

In Abrar's setup this bot sits in a private Discord server as a remote control for the laptop: run a Python or shell script that lives in the home directory and see its output, get a quick web search result, or have the bot read something out loud in a voice channel. It is the explicit-command counterpart to `abrar-assistant`, which routes free text through a language model instead.

## How it works

`bot.py` loads `.env` (by absolute path), instantiates every service once at start-up, and registers the commands below. Each command does a little validation, calls one service method and posts the result, truncating anything longer than 1900 characters to stay under Discord's message limit.

### Commands

| Command | Behaviour |
|---|---|
| `!run <path>` | Accepts only paths under the home directory that exist. Picks an interpreter by extension: `.py` python3, `.js` node, `.go` go run, `.rb` ruby, `.sh` bash; `.c`/`.cpp` are compiled with gcc/g++ to `temp_exec` and executed through the shell. 15-second timeout; stdout is posted, falling back to stderr. |
| `!analyze` (with an image attached) | Saves the attachment to `data/` and sends it to the local Ollama model configured in `ImageAnalysisService` with the prompt "Describe this image". |
| `!search <query>` | Google Custom Search JSON API (`GOOGLE_SEARCH_API_KEY` + `GOOGLE_CSE_ID`); posts the top 3 titles and links. |
| `!create_doc <title>` / `!create_sheet <title>` / `!create_slide <title>` | Creates an empty document through the Docs, Sheets or Slides API using a service-account key and replies with its URL. |
| `!create_pdf <text>` | Builds a one-line PDF with FPDF (`output.pdf`) and uploads it. |
| `!join` / `!leave` | Connects the bot to the caller's current voice channel, or disconnects. |
| `!speak <text>` | Generates speech with ElevenLabs, saves `speech.mp3`, and plays it in the connected voice channel through `discord.FFmpegPCMAudio`. |
| `!quiz` | Runs a three-question quiz, but on the server's own terminal with `input()`, not in Discord (see limitations). |

### Services

| File | Role |
|---|---|
| `services/shell_service.py` | `CloudShellService`: authenticates with a service-account key and starts a Google Cloud Shell session via the `cloudshell` API. It returns a confirmation string rather than running the command and is not attached to any command. |
| `services/image_service.py` | `ollama.chat` with an `images` list; the model name is a constant in the file. |
| `services/search_service.py` | Google Custom Search request and formatting. |
| `services/google_service.py` | Builds Docs/Sheets/Slides clients from the service-account file named in the corresponding env variable. |
| `services/voice_service.py` | ElevenLabs client, `generate(text, voice)` streamed to a file. |
| `services/pdf_service.py` | `create_pdf` with FPDF and an unused `read_pdf` with PyPDF2. |
| `services/quiz_service.py` | Hard-coded questions, terminal I/O, score counting. |
| `commands/quiz_command.py` | Thin wrapper that calls `QuizService.run_quiz()`. |

A `read_file` coroutine in `bot.py` (home-directory-scoped file reader) exists but has no `@bot.command` decorator, so it is not reachable from Discord. The `utils/` folder is empty.

## Setup

Requirements: Python 3.10+, FFmpeg on `PATH` (for voice playback), a local [Ollama](https://ollama.com) server with an image-capable model, a Discord application with the Message Content intent, a Google Cloud service account with the Docs/Sheets/Slides APIs enabled, a Google Programmable Search Engine, an ElevenLabs account.

```bash
cd ~/Workspace/SystemControlBot
python3 -m venv venv && source venv/bin/activate
pip install discord.py[voice] python-dotenv ollama requests \
            google-api-python-client google-auth elevenlabs fpdf PyPDF2
mkdir -p data
```

`.env` (the path is hard-coded in `bot.py`, keep it in the project root):

```ini
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_CLIENT_ID=000000000000000000
DISCORD_CLIENT_SECRET=your-client-secret
DISCORD_PUBLIC_KEY=your-public-key
ELEVENLABS_API_KEY=your-elevenlabs-key
ELEVENLABS_VOICE_ID=your-voice-id
GOOGLE_SHELL_API_KEY_PATH=~/secrets/service-account.json
GOOGLE_DOCS_API_KEY_PATH=~/secrets/service-account.json
GOOGLE_SPREADSHEETS_API_KEY_PATH=~/secrets/service-account.json
GOOGLE_SLIDES_API_KEY_PATH=~/secrets/service-account.json
GOOGLE_CSE_ID=your-cse-id
GOOGLE_SEARCH_API_KEY=your-search-key
```

`GOOGLE_SHELL_API_KEY_PATH` must point at a readable file even though no command uses Cloud Shell, because the service is constructed at start-up.

## Usage

```bash
source venv/bin/activate
python bot.py
```

In Discord:

```
!run ~/scripts/report.py
!run ~/scripts/hello.c
!search raspberry pi 5 power draw
!create_sheet Monthly budget
!create_pdf Shopping list for Friday
(attach a photo) !analyze
!join
!speak The build finished successfully.
!leave
```

## Project structure

```
SystemControlBot/
├── bot.py                     # command definitions and service wiring
├── commands/
│   └── quiz_command.py
├── services/
│   ├── shell_service.py       # Cloud Shell session starter (unused by commands)
│   ├── image_service.py       # Ollama image description
│   ├── search_service.py      # Google Custom Search
│   ├── google_service.py      # Docs / Sheets / Slides creation
│   ├── voice_service.py       # ElevenLabs TTS
│   ├── pdf_service.py         # FPDF / PyPDF2
│   └── quiz_service.py        # terminal quiz
├── utils/                     # empty
└── data/                      # saved image attachments (runtime)
```

## Limitations and notes

- No permission checks: any member of a channel the bot reads can run scripts from the home directory. Keep it in a private server.
- `!run` only guards the path prefix; a script can still do anything the bot's user can. The 15-second timeout kills long scripts.
- `!quiz` blocks the whole bot waiting for keyboard input on the host terminal; it is a leftover from a CLI prototype.
- The image model named in `image_service.py` must support image input; a text-only model will error.
- Google documents are created empty, with only a title.
- `speech.mp3`, `output.pdf` and `temp_exec` are written to the current working directory and overwritten on each call.
- Cloud Shell execution is not implemented; `CloudShellService` only opens a session.
