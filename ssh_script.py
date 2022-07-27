import paramiko, yaml, pathlib


def get_ssh_config():
    crr_parent_path = pathlib.Path(__file__).parent.parent.resolve()
    print(crr_parent_path)
    with open(f"{crr_parent_path}/ssh_python/ssh.conf.yml", "r") as f:
        config = yaml.safe_load(f)
        return { "ip": config.get("ip"), "username": config.get("username"), "password": config.get("password") }

def get_bucardo_list():
    try:
        ssh_c = get_ssh_config()
        ip = ssh_c.get("ip")
        username = ssh_c.get("username")
        password = ssh_c.get("password")

        ssh = paramiko.SSHClient()

        # Load SSH host keys.
        ssh.load_system_host_keys()
        # Add SSH host key automatically if needed.
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to router using username/password authentication.
        ssh.connect(ip, username=username, password=password,look_for_keys=False)

        # Run command.
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker exec postgres_bucardo bucardo status")

        output = ssh_stdout.readlines()
        output.pop(0) # PID header
        output.pop(0) # Names' header
        output.pop(0) # Lines
        
        # Close connection.
        ssh.close()

        row_list = []
        server_list = []
        for item in output:
            lista_pipe = item.split('|')
            for i in lista_pipe:
                row_list.append(i.strip())
            server_list.append({
                'name' : row_list[0]
                , 'state': row_list[1]
                , 'last_good': row_list[2]
                , 'time': row_list[3]
                , 'last_i_d': row_list[4]
                , 'last_bad': row_list[5]
                , 'time': row_list[6]
            })
            row_list = []

        return server_list
    except:
        print("An exception occurred")
        return "error"

print(get_bucardo_list())
