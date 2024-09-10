import paramiko
import subprocess

class Mission:

    name: str
    port: int
    number: int
    targets : list

    def __init__(self, name, port, mission_number) -> None:
        
        self.our_team_number = 2
        self.targets = list()
        self.name = name
        self.port = port
        self.number = mission_number

        self.targets = [f"10.1.{team_number}.{mission_number}" for team_number in range(1,9) if team_number != self.our_team_number]
        

    def submit_remote(self) -> str:

        ssh = paramiko.SSHClient()
        ssh.load_host_keys("/home/dragos/.ssh/known_hosts")
        ssh.connect(f"10.1.1.54", username="cyberman", password="Parolaputernica")
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(f"submit_atc 12345")
        ssh.close()
        return ssh_stdout.read().decode()
    

    def submit_local(self) -> str:
        process = subprocess.Popen("submit_atc 12345")
        stdout, stderr = process.communicate()
        return stdout.decode()