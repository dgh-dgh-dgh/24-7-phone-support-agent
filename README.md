# 24/7 Phone Support Agent

An AI phone support line for a film screening platform, built on **ElevenLabs Agents** and **Twilio**. Callers ring a real phone number at any hour. The agent answers their questions and looks up live data through a **Python (FastAPI) webhook**, for example "What's showing in my city?".

All films, venues and dates are fictional sample data.

## Architecture

```
Caller -> Twilio phone number (or dashboard test)
   -> ElevenLabs agent (speech-to-text, LLM, text-to-speech)
      -> webhook tool: GET /screenings?city=...   (X-Api-Key header)
         -> FastAPI service -> data/screenings.json
      <- JSON with a short "summary" written to be spoken
   <- spoken answer
```

**Design choices**
- **Answer written for speech.** The service returns a `summary` sentence, so the agent doesn't have to turn raw JSON into speech.
- **Shared-secret header (`X-Api-Key`).** Only the agent can call the endpoint.
- **Data behind one function (`load_screenings`).** Swapping the JSON file for a real API or database touches one place.

## Project structure

```
app/main.py            FastAPI webhook service
data/screenings.json   Sample data
scripts/hello_voice.py Step 1 smoke test: text-to-speech to MP3
tests/test_main.py     pytest suite
```

## Step 1 - Local setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then fill in your keys
```

Create an API key in the ElevenLabs dashboard and put it in `.env`. Set `WEBHOOK_SECRET` to a long random string, for example the output of `python -c "import secrets; print(secrets.token_urlsafe(32))"`.

```bash
python scripts/hello_voice.py      # writes hello.mp3
pytest                             # 6 tests should pass
```

## Step 2 - Run the webhook service

```bash
uvicorn app.main:app --reload --port 8000
```

Check it at `http://localhost:8000/screenings?city=Austin`. If `WEBHOOK_SECRET` is set, add the header, or use the interactive docs at `http://localhost:8000/docs`.

## Step 3 - Expose it publicly

ElevenLabs' servers need a public HTTPS URL. For testing, use a tunnel such as `ngrok http 8000`. A tunnel on your laptop isn't 24/7, so for the live line deploy the service to an always-on host such as Render, Railway or Fly.io. Check that the plan you pick doesn't sleep when idle, because a cold start means dead air on the call:
- start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- set `WEBHOOK_SECRET` as an environment variable on the host

## Step 4 - Create the agent (ElevenLabs dashboard)

1. Create a new agent.
2. Use this system prompt:
   > You are the 24/7 phone support agent for an independent film screening platform. Open by saying you're an AI assistant. When a caller asks what is showing in a city, always call the `get_screenings` tool with that city, then read back the `summary` field naturally. If the caller doesn't name a city, ask for one. If you can't help, say so plainly and suggest they email support. Keep answers short and conversational, because this is a phone call.
3. Add the webhook tool under **Agent -> Add Tool -> Webhook**:

| Field | Value |
|---|---|
| Name | `get_screenings` |
| Description | Look up upcoming film screenings in a city. |
| Method | GET |
| URL | `https://<your-public-url>/screenings` |
| Query parameter | `city` (string, LLM Prompt): "City the caller is asking about" |
| Header | `X-Api-Key` = your `WEBHOOK_SECRET` (store it as a secret) |

4. Test by voice in the dashboard. The requests show up in the uvicorn logs.

Docs: [Webhook tools](https://elevenlabs.io/docs/agents-platform/customization/tools/server-tools)

## Step 5 - Phone number

Buy a voice-capable number in Twilio. In ElevenAgents, open **Phone Numbers**, import the number with your Twilio SID and token, and assign the agent to it.

Docs: [Twilio native integration](https://elevenlabs.io/docs/eleven-agents/phone-numbers/twilio-integration/native-integration)

## Next steps

- Add a `film` filter and a date range.
- Add a second tool, `send_sms_link`, that texts a booking link.
- Create the tool and agent from Python with the ElevenLabs SDK, so the setup can be reproduced. See the Python example in the webhook tools docs.
