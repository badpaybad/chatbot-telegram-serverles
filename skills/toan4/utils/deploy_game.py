import paramiko
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
try:
    from config_dunp import sftp_host, sftp_port, sftp_username, sftp_password
except ImportError:
    print("Cannot import config_dunp! Please make sure it exists at the root.")
    sys.exit(1)

def upload_game_via_sftp(folder_name):
    local_game_folder = os.path.join(os.path.dirname(__file__), f'../../../games/toanlop4/{folder_name}')
    remote_target_folder = f'/work/nginxstaticfile/games/maths/{folder_name}'
    
    print(f"Connecting to {sftp_host}:{sftp_port} as {sftp_username}...")
    
    transport = paramiko.Transport((sftp_host, int(sftp_port)))
    transport.connect(username=sftp_username, password=sftp_password)
    
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    try:
        sftp.mkdir(remote_target_folder)
    except IOError:
        pass # Directory probably already exists
        
    for item in os.listdir(local_game_folder):
        local_path = os.path.join(local_game_folder, item)
        remote_path = os.path.join(remote_target_folder, item)
        
        if os.path.isfile(local_path):
            print(f"Uploading {item}...")
            sftp.put(local_path, remote_path)
            
    sftp.close()
    transport.close()
    
    print("Upload completed successfully!")
    print(f"Game URL: https://static.airobotics.vn/games/maths/{folder_name}/")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python deploy_game.py <folder_name>")
        sys.exit(1)
    upload_game_via_sftp(sys.argv[1])
