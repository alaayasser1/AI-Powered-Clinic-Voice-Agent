# AI-Powered Clinic Voice Agent 

An AI-powered voice assistant that automates clinic interactions and appointment management through natural voice conversations.

  Currently in Development

## Features

- Voice Interaction: Natural voice conversations with patients in Egyptian Arabic.
- Appointment Availability: Check available slots by date and doctor.
- Appointment Booking: Book appointments and store patient details.
- Appointment Cancellation:Cancel existing bookings and restore slots to availability.
- Appointment Rescheduling:Move bookings to another available slot.
- Database Integration:Manage appointments and booking statuses using SQLite.
- Double-Booking Prevention: Ensure unavailable slots cannot be booked twice.

# Tech Stack

- Python
- LiveKit Agents
- Google Gemma 4
- AssemblyAI (STT)
- Fish Audio (TTS)
- SQLite
- Git & GitHub

# How It Works

1. The patient speaks to the voice agent.
2. The agent understands the request using speech recognition and an LLM.
3. It calls the appropriate appointment management tool.
4. SQLite processes the requested operation.
5. The agent responds to the patient with the result.

# Getting Started

```bash
git clone YOUR_REPOSITORY_URL
cd clinic-voice-agent
uv sync
```

Configure the required API credentials in your environment file, then run:

```bash
lk agent dev
```

# Roadmap

- WhatsApp appointment confirmations.
- Automated appointment reminders.
- Missed-appointment follow-ups.
- Clinic management dashboard.
