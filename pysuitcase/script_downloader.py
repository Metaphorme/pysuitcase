import click
import requests
import subprocess
import sys
import os
from urllib.parse import urlparse

def bootstrap_pip(python_exe_path, work_dir, mirror=None):
    """在新的 Python 环境中，从零开始安装 pip。"""
    click.echo("\n-------------------------------------")
    click.secho("Bootstrapping pip...", fg='cyan', bold=True)
    
    get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
    get_pip_path = os.path.join(work_dir, "get-pip.py")

    try:
        click.echo(f"Downloading {get_pip_url}...")
        response = requests.get(get_pip_url)
        response.raise_for_status()
        with open(get_pip_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
    except requests.RequestException as e:
        click.secho(f"Error downloading get-pip.py: {e}", fg='red')
        sys.exit(1)

    command = [python_exe_path, get_pip_path]
    if mirror:
        mirror_host = urlparse(mirror).hostname
        command.extend(["--no-cache-dir", "-i", mirror, "--trusted-host", mirror_host])
        
    click.echo(f"Running command: {' '.join(command)}")
    try:
        process = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='mbcs',
            errors='ignore'
        )
        click.echo(process.stdout)
        click.secho("pip bootstrapped successfully!", fg='green')
    except subprocess.CalledProcessError as e:
        click.secho("Failed to bootstrap pip!", fg='red', bold=True)
        click.echo(e.stdout)
        click.secho(e.stderr, fg='red')
        sys.exit(1)
    finally:
        if os.path.exists(get_pip_path):
            os.remove(get_pip_path)


def install_dependencies(python_exe_path, requirements_path, mirror=None):
    """分两步在新环境中安装依赖：先装构建工具，再装其他所有包。"""
    if not os.path.exists(requirements_path):
        click.secho(f"Warning: '{requirements_path}' not found. Skipping dependency installation.", fg='yellow')
        return True

    # --- 步骤 1: 安装构建工具 ---
    click.echo("\n-------------------------------------")
    click.secho("Step 1/2: Installing build essentials (setuptools, wheel)...", fg='cyan', bold=True)
    
    build_essentials = ['setuptools', 'wheel']
    command_build = [python_exe_path, "-m", "pip", "install"] + build_essentials
    if mirror:
        mirror_host = urlparse(mirror).hostname
        command_build.extend(["-i", mirror, "--trusted-host", mirror_host])
    
    click.echo(f"Running command: {' '.join(command_build)}")
    try:
        subprocess.run(
            command_build, check=True, capture_output=True, text=True,
            encoding='mbcs', errors='ignore'
        )
        click.secho("Build essentials installed successfully.", fg='green')
    except subprocess.CalledProcessError as e:
        click.secho("Failed to install build essentials!", fg='red', bold=True)
        click.echo(e.stdout)
        click.secho(e.stderr, fg='red')
        return False

    # --- 步骤 2: 安装 requirements.txt 中的所有包 ---
    click.echo("\n-------------------------------------")
    click.secho(f"Step 2/2: Installing packages from {os.path.basename(requirements_path)}...", fg='cyan', bold=True)
    
    command_reqs = [
        python_exe_path,
        "-m", "pip", "install", "--no-cache-dir", "--upgrade",
        "-r", requirements_path
    ]
    
    # 注意：-r 文件里的 --extra-index-url 会被 pip 自动处理，但我们仍然需要为从主源下载的包提供镜像
    if mirror:
        mirror_host = urlparse(mirror).hostname
        command_reqs.extend(["-i", mirror, "--trusted-host", mirror_host])
    
    click.echo(f"Running command: {' '.join(command_reqs)}")
    try:
        process = subprocess.run(
            command_reqs, capture_output=True, text=True, check=True,
            encoding='mbcs', errors='ignore'
        )
        click.echo(process.stdout)
        click.secho("Dependencies installed successfully!", fg='green')
        return True
    except subprocess.CalledProcessError as e:
        click.secho("An error occurred during dependency installation:", fg='red')
        click.echo(e.stdout)
        click.secho(e.stderr, fg='red')
        return False

def download_and_run_ps_script(version, arch, project_dir):
    """在指定的项目目录中，下载并执行 PythonEmbed4Win.ps1 脚本。"""
    script_path = os.path.join(project_dir, "PythonEmbed4Win.ps1")
    script_url = "https://raw.githubusercontent.com/jtmoon79/PythonEmbed4Win/main/PythonEmbed4Win.ps1"

    try:
        click.echo(f"Downloading PowerShell script to {project_dir}...")
        response = requests.get(script_url)
        response.raise_for_status()
        with open(script_path, 'w', encoding='utf-8-sig') as f:
            f.write(response.text)
        click.secho("Download complete.", fg='green')
    except requests.RequestException as e:
        click.secho(f"Error downloading script: {e}", fg='red')
        sys.exit(1)

    python_install_path = os.path.join(project_dir, f"python-{version}-embed-{arch}")
    
    command = [
        "powershell",
        "-ExecutionPolicy", "Bypass",
        "-File", script_path,
        "-Version", version,
        "-Arch", arch,
        "-Path", python_install_path,
        "-SkipExec"
    ]

    click.echo(f"Running command: {' '.join(command)}")
    click.echo(f"Attempting to install Python into: {python_install_path}")
    
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=project_dir,
            encoding='mbcs',
            errors='ignore'
        )
        click.echo(process.stdout)
        click.secho(f"\nEmbedded Python downloaded successfully to {python_install_path}!", fg='green')
        return python_install_path
    except subprocess.CalledProcessError as e:
        click.secho("An error occurred while running the PowerShell script:", fg='red')
        click.secho(e.stderr, fg='red')
        click.secho("\nHint: Make sure you have 'Desktop development with C++' installed via Visual Studio Installer.", fg='yellow')
        sys.exit(1)
    finally:
        if os.path.exists(script_path):
            click.echo(f"Cleaning up {os.path.basename(script_path)}...")
            os.remove(script_path)