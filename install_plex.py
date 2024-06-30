import os
import subprocess
import getpass

def install_docker():
    subprocess.run(['sudo', 'apt', 'update'], check=True)
    subprocess.run(['sudo', 'apt', 'install', '-y', 'docker.io'], check=True)
    subprocess.run(['sudo', 'systemctl', 'start', 'docker'], check=True)
    subprocess.run(['sudo', 'systemctl', 'enable', 'docker'], check=True)

def install_docker_compose():
    subprocess.run(['sudo', 'apt', 'install', '-y', 'docker-compose'], check=True)

def get_input(prompt_text):
    return input(prompt_text)

def edit_fstab(network_path, local_dir, username, password):
    fstab_entry = f"{network_path} {local_dir} cifs username={username},password={password},uid=1000,gid=1000 0 0\n"
    with open('/etc/fstab', 'a') as fstab:
        fstab.write(fstab_entry)
    subprocess.run(['sudo', 'mount', '-a'], check=True)

def create_docker_compose_yaml(dir_path, plex_claim, library_path, tvseries_path, movies_path):
    docker_compose_content = f"""
version: '3'
services:
  plex:
    image: lscr.io/linuxserver/plex:latest
    container_name: plex
    network_mode: bridge
    ports:
      - "32400:32400/tcp"
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
      - VERSION=docker
      - PLEX_CLAIM={plex_claim}
    volumes:
      - {library_path}:/config
      - {tvseries_path}:/tv
      - {movies_path}:/movies
    restart: unless-stopped
"""
    with open(os.path.join(dir_path, 'docker-compose.yml'), 'w') as file:
        file.write(docker_compose_content)

def main():
    # Install Docker and Docker-Compose
    install_docker()
    install_docker_compose()

    # Get user inputs
    dir_path = get_input("Enter the path where you want to create the directory: ")
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    network_path = get_input("Enter the network path (e.g., //10.10.10.10/Plex): ")
    local_dir = get_input("Enter the local directory path (e.g., /PlexMedia): ")
    username = get_input("Enter the username: ")
    password = getpass.getpass("Enter the password: ")

    # Edit /etc/fstab
    edit_fstab(network_path, local_dir, username, password)

    # Prompt for Plex claim and paths
    plex_claim = get_input("Enter the Plex claim token (leave blank if not applicable): ")
    library_path = os.path.join(dir_path, 'library')
    tvseries_path = os.path.join(dir_path, 'tvseries')
    movies_path = os.path.join(dir_path, 'movies')

    # Create Docker-Compose file
    create_docker_compose_yaml(dir_path, plex_claim, library_path, tvseries_path, movies_path)

    # Run Docker-Compose up
    subprocess.run(['sudo', 'docker-compose', 'up', '-d'], cwd=dir_path, check=True)

if __name__ == "__main__":
    main()
