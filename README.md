# Python Chatroom Application

A robust, real-time chat application built with Python, featuring a graphical user interface (GUI) and support for private messaging and file sharing.

## Features

- **Real-time Messaging**: Instant communication between connected clients.
- **Server/Client Architecture**: Run as a central server or a client connecting to the server.
- **Graphical User Interface**: Built with `tkinter` for a user-friendly experience.
- **Private Messaging**: Send secure private messages to specific users.
- **File Sharing**: Support for sending and receiving files (Images, Videos, Audio, etc.).
- **Modern UI**: Dark mode themed interface with color-coded messages.

## Requirements

- Python 3.x
- `tkinter` (usually included with standard Python installations)

## Installation

1. Clone the repository or download the source code.
2. Ensure you have Python installed.

## Usage

The application is contained within a single script `chatroom.py` that can function as either the server or the client.

### Starting the Server

1. Open a terminal.
2. Run the script:
   ```bash
   python chatroom.py
   ```
3. When prompted "Start as (server/client):", type `server` and press Enter.
4. The server will start on `127.0.0.1:12345`.

### Connecting a Client

1. Open a new terminal window.
2. Run the script:
   ```bash
   python chatroom.py
   ```
3. When prompted "Start as (server/client):", type `client` and press Enter.
4. Enter your desired alias (username) in the popup dialog.
5. Start chatting!

## File Transfer

- Click the **📎 Media** button to select and send a file.
- Received files are saved in the current directory with a `received_` prefix.

## Private Messaging

- Click the **🔒 Private** button.
- Enter the recipient's alias and your message to send it privately.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
