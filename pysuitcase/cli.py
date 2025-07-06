import click
import sys
import os
import platform
import shlex

from .script_downloader import download_and_run_ps_script, bootstrap_pip, install_dependencies
from .compiler import compile_launcher, encrypt_code

def _print_summary(params):
    """打印格式化的配置摘要。"""
    click.echo("\n-------------------------------------")
    click.secho("Final Configuration Summary:", fg='green', bold=True)
    click.echo(f"  - Project Directory:    {params.get('project_dir')}")
    click.echo(f"  - Application Folder:   {os.path.join(params.get('project_dir', ''), params.get('app_folder', ''))}")
    click.echo(f"  - Main Script:          {params.get('main_script')}")
    if params.get('encrypt'):
        click.secho(f"  - Python Version:       {params['python_version']} (Locked to Host for Encryption)", fg='red', bold=True)
        click.secho(f"  - Architecture:         {params['arch']} (Locked to Host for Encryption)", fg='red', bold=True)
    else:
        click.secho(f"  - Python Version:       {params['python_version']} (Target)", fg='cyan')
        click.secho(f"  - Architecture:         {params['arch']} (Target)", fg='cyan')
    click.echo(f"  - Requirements File:    {os.path.join(params.get('project_dir', ''), params.get('app_folder', ''), params.get('requirements_file', ''))}")
    click.echo(f"  - PyPI Mirror:          {params.get('mirror') or 'Not specified'}")
    click.echo(f"  - Custom Icon:          {params.get('icon') or 'Default'}")
    click.secho(f"  - Launcher Mode:        {'Windowless' if params.get('no_window') else 'Console'}", fg='magenta')
    click.echo(f"  - Encrypt Source Code:  {'Yes' if params.get('encrypt') else 'No'}")
    if params.get('encrypt'):
        fg_color = 'red' if params.get('delete_source_on_encrypt') else 'green'
        click.secho(f"  - Delete Source Files:  {'YES' if params.get('delete_source_on_encrypt') else 'NO'}", fg=fg_color, bold=True)
    click.echo("-------------------------------------\n")

def execute_build(params):
    """执行核心打包逻辑。"""
    _print_summary(params)
    if params.get('_is_interactive'):
        if not click.confirm("Proceed with this configuration?", default=True, abort=True):
            return
    click.secho("\nStarting packaging process...", bold=True)
    python_embed_path = download_and_run_ps_script(version=params['python_version'], arch=params['arch'], project_dir=params['project_dir'])
    if python_embed_path and os.path.exists(python_embed_path):
        python_exe = os.path.join(python_embed_path, 'python.exe')
        app_dir_path = os.path.join(params['project_dir'], params['app_folder'])
        requirements_path = os.path.join(app_dir_path, params['requirements_file'])
        bootstrap_pip(python_exe, work_dir=python_embed_path, mirror=params['mirror'])
        if not install_dependencies(python_exe, requirements_path, params['mirror']):
            click.secho("Failed to install dependencies. Aborting.", fg='red', bold=True); sys.exit(1)
        if params['encrypt']:
            encrypt_code(app_dir_path, delete_source=params['delete_source_on_encrypt'])
        click.echo("\nAll preparations are complete. Starting final compilation...")
        compile_launcher(
            project_dir=params['project_dir'],
            app_folder=params['app_folder'],
            main_script=params['main_script'],
            python_version=params['python_version'],
            arch=params['arch'],
            requirements_file=params['requirements_file'],
            icon_path=params['icon'],
            no_window=params.get('no_window', False)
        )

def generate_reproducible_command(params):
    """根据参数生成可复现的命令行字符串。"""
    def win_quote(value):
        """如果字符串包含空格，则为其添加引号以用于 Windows 命令行。"""
        s = str(value)
        if ' ' in s and not (s.startswith('"') and s.endswith('"')):
            return f'"{s}"'
        # 如果字符串没有空格，则按原样返回，避免不必要的引号。
        return s.strip("'")

    # 从基本命令和项目目录开始
    command = [f"pysuitcase {win_quote(params['project_dir'])}"]

    # 处理所有带值的选项
    valued_options = [
        'app_folder', 'main_script', 'requirements_file', 'python_version', 
        'arch', 'icon', 'mirror'
    ]
    for key in valued_options:
        value = params.get(key)
        if value is not None:
            command.append(f"--{key.replace('_', '-')} {win_quote(value)}")
            
    # 显式处理所有布尔标志选项
    if params.get('encrypt'):
        command.append('--encrypt')
    if params.get('delete_source_on_encrypt'):
        # 为这个危险的标志保留特殊样式
        command.append(click.style('--delete-source-on-encrypt', fg='red', bold=True))
    if params.get('no_window'):
        command.append('--no-window')
        
    return ' '.join(command)

def run_interactive_mode(params):
    """以交互方式引导用户完成所有选项。"""
    click.echo("Entering interactive mode...")
    params['project_dir'] = click.prompt("Enter the path to your project's root directory", type=click.Path(exists=True, file_okay=False, resolve_path=True))
    params['encrypt'] = click.confirm("Encrypt Python source code for protection?", default=False)
    if params['encrypt']:
        click.secho(f"Encryption enabled. Python version locked to host: {params['python_version']} ({params['arch']})", fg='cyan')
        if click.confirm(click.style("DELETE original .py source files after encryption?", fg='red', bold=True), default=False):
            if click.confirm(click.style("This action is IRREVERSIBLE. Are you sure?", fg='red', bold=True), default=False):
                params['delete_source_on_encrypt'] = True
    else:
        click.secho("Encryption disabled. You can specify a target Python version.", fg='yellow')
        host_version = params['python_version']
        host_arch = params['arch']
        params['python_version'] = click.prompt(f"Enter target Python version (Default: {host_version})", default=host_version, show_default=False)
        params['arch'] = click.prompt(f"Enter target architecture (Default: {host_arch})", type=click.Choice(['amd64', 'win32', 'arm64']), default=host_arch, show_default=False)
    default_app_folder = 'app'
    params['app_folder'] = click.prompt(f"Enter the name of your source code folder (Default: {default_app_folder})", default=default_app_folder, show_default=False)
    default_main_script = 'app.py'
    params['main_script'] = click.prompt(f"Enter the name of your main script (Default: {default_main_script})", default=default_main_script, show_default=False)
    default_reqs = 'requirements.txt'
    params['requirements_file'] = click.prompt(f"Enter the name of your requirements file (Default: {default_reqs})", default=default_reqs, show_default=False)
    if click.confirm('Do you want to use a PyPI mirror? (Recommended in some regions)', default=False):
        params['mirror'] = click.prompt('Enter the PyPI mirror URL', default='https://pypi.tuna.tsinghua.edu.cn/simple')
    else:
        params['mirror'] = None
    icon_path_str = click.prompt("Enter path to a custom .ico file (or press Enter for default)", default='', show_default=False, type=str)
    if icon_path_str:
        if not os.path.exists(icon_path_str):
            click.secho(f"Error: Icon file not found at '{icon_path_str}'. Please provide a valid path.", fg='red'); sys.exit(1)
        params['icon'] = icon_path_str
    else:
        params['icon'] = None
    
    # 修正了 'no_window' 提示的位置
    params['no_window'] = click.confirm("Use windowless mode?", default=False)

    params['_is_interactive'] = True
    execute_build(params)
    click.secho("\n🎉 PySuitcase packaging process completed successfully! 🎉", fg='cyan', bold=True)
    click.echo("\nTo run this again without interactive prompts, use the following command:")
    click.echo(generate_reproducible_command(params))

def run_direct_mode(params):
    """验证后直接使用提供的参数运行。"""
    if params.get('encrypt') and (params.get('python_version') is not None or params.get('arch') is not None):
        click.secho("Error: When using --encrypt, you cannot specify --python-version or --arch.", fg='red', bold=True)
        click.secho("Encryption requires using the host's Python environment.", fg='yellow'); sys.exit(1)
    
    # 为直接模式填充默认值
    if params.get('app_folder') is None: params['app_folder'] = 'app'
    if params.get('main_script') is None: params['main_script'] = 'app.py'
    if params.get('requirements_file') is None: params['requirements_file'] = 'requirements.txt'

    click.echo("Running in direct mode...")
    execute_build(params)
    click.secho("\n🎉 PySuitcase packaging process completed successfully! 🎉", fg='cyan', bold=True)

@click.command(context_settings=dict(ignore_unknown_options=True, help_option_names=['-h', '--help']))
@click.argument('project_dir', type=click.Path(exists=True, file_okay=False, resolve_path=True), required=False)
@click.option('--app-folder', default=None, help='Name of the folder containing your source code.')
@click.option('--main-script', default=None, help='Name of the main script file.')
@click.option('--requirements-file', default=None, help='Name of the requirements file.')
@click.option('--python-version', default=None, help='Target Python version. Incompatible with --encrypt.')
@click.option('--arch', default=None, type=click.Choice(['amd64', 'win32', 'arm64']), help='Target architecture. Incompatible with --encrypt.')
@click.option('--icon', default=None, help='Path to a .ico file for the launcher.')
@click.option('--mirror', default=None, help='PyPI mirror URL.')
@click.option('--encrypt', is_flag=True, help='Encrypt source code. Locks Python version to host version.')
@click.option('--delete-source-on-encrypt', is_flag=True, help='[DANGEROUS] Delete .py source files after encryption.')
@click.option('--no-window', is_flag=True, help='Use a windowless launcher for the final executable.')
@click.pass_context
def main(ctx, **kwargs):
    """
    将 PROJECT_DIR 中的 Python 项目打包成一个独立的可执行文件。
    """
    params = kwargs
    host_python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    host_arch = 'amd64' if platform.architecture()[0] == '64bit' else 'win32'
    
    if params.get('python_version') is None:
        params['python_version'] = host_python_version
    if params.get('arch') is None:
        params['arch'] = host_arch
        
    params['_is_interactive'] = False
    
    if params.get('project_dir') is None:
        params['python_version'] = host_python_version
        params['arch'] = host_arch
        run_interactive_mode(params)
    else:
        run_direct_mode(params)
