# Grais Reminder

A simple reminder application that plays a sound and shows a notification every hour between 8am and 8pm to remind you to check back with the Grais system.

## Requirements

- Node.js
- pnpm (preferred) or npm

## Installation

All dependencies are managed with pnpm:

```bash
pnpm install
```

## Usage

Start the reminder application:

```bash
pnpm start
```

The application will:

- Run in the foreground (keep the terminal window open)
- Play a sound and show a notification every hour between 8am and 8pm
- Show startup messages and logging information in the terminal

## Running in the background

To run the application in the background:

### macOS/Linux

```bash
nohup pnpm start > reminder.log 2>&1 &
```

### Windows

Use a tool like [PM2](https://pm2.keymetrics.io/) or run in a separate terminal.

## Stopping the application

If running in the foreground, press `Ctrl+C` in the terminal window.

If running in the background with the command above, find the process ID and kill it:

```bash
ps aux | grep node
kill [PID]
```
