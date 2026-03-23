# PySuitcase

![Python Versions](https://img.shields.io/badge/3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue?logo=Python&logoColor=yellow&label=Python&labelColor=blue&color=white)

[English document](./README.md)

**在 Windows 平台，像分发绿色软件一样轻松分发和部署您的 Python 应用程序。**

PySuitcase 为 Windows 平台提供了一种全新的 Python 程序分发方案。它能将您的 Python 项目完整打包到一个独立的文件夹中，该文件夹内嵌了所有依赖库和独立的 Python 解释器。用户无需在本地安装 Python 或进行任何复杂的环境配置，解压即可直接运行。

## ✨ 项目特色

* **真正的“绿色软件”**：无需安装，不写入注册表，没有复杂的配置。用户下载解压后即可立即使用，就像使用任何便携式应用一样。
* **攻克打包难题**：轻松封装包含 `PyTorch`、`PyTorch Geometric`、`PyQt5` 等大型复杂库的项目。这些库通常是 `Pyinstaller`、`Nuitka` 等传统工具的“噩梦”。
* **源代码保护**：提供可选的代码加密功能，使用 `Cython` 将您的 `.py` 文件编译成 `.pyd` 二进制文件，有效保护您的知识产权。
* **自动化流程**：从下载嵌入式 Python、安装依赖、到编译启动器，所有繁琐的步骤都由 PySuitcase 自动化完成。
* **灵活自定义**：支持自定义应用程序图标、指定国内 PyPI 镜像源以加速依赖下载，并可选择是否在加密后删除源文件。

## 📋 使用说明

### 第 1 步：环境准备

1.  **安装 MSVC (Microsoft Visual C++ Build Tools)**
    * 下载并运行 [Visual Studio Build Tools 安装程序](https://aka.ms/vs/17/release/vs_buildtools.exe)。
    * 勾选 **“使用 C++ 的桌面开发”**，然后进行安装。这是编译启动器所必需的。

2.  **准备一个和目标 Python 版本一致的环境**
    * 建议使用您的开发环境安装 PySuitcase，但这样会在您的开发环境中引入 PySuitcase；
    * 您可以在一个全新、和目标 Python 版本一致、仅安装 PySuitcase 的 Python 环境中使用 PySuitcase 的全部功能；
    * 如果您运行 PySuitcase 的环境与目标 Python 版本不一致，则无法使用代码加密的功能。
    
    在您选定的环境中，通过 GitHub 安装 PySuitcase：
    ```bash
    pip install git+https://github.com/metaphorme/pysuitcase.git
    ```

### 第 2 步：启动专用命令行工具

为了让 PySuitcase 能够找到 C++ 编译器 (`cl.exe`)，您必须从 **Visual Studio 专用命令行提示符** 运行它。

* 从“开始”菜单中找到并打开 **"x64 Native Tools Command Prompt for VS 2022"** (或您安装的 VS 版本对应的工具)。

* 或者，在常规的 `cmd` 或 `powershell` 窗口中，运行以下命令来加载所需的环境变量：
    ```cmd
    call "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
    ```
    *> 注意：上述路径可能因您的 Visual Studio 安装位置和版本而异。*

之后，激活您的虚拟环境（venv 或 conda environment）。

### 第 3 步：组织您的项目文件

PySuitcase 期望您的项目遵循一个简单的目录结构。假设您的项目名为 `MyAwesomeApp`：

```
MyAwesomeApp/              \<-- 项目根目录
└── app/                   \<-- 存放项目 Python 源代码的文件夹
    ├── app.py             \<-- 您的主程序入口
    ├── requirements.txt   \<-- 项目依赖列表
    └── *.py               \<-- 其他脚本
```

* **项目根目录 (`MyAwesomeApp/`)**：在发行时，您可以直接将此目录打包发行。编译出的启动器名称将为 `<MyAwesomeApp>.exe`。
* **源代码文件夹 (`app/`)**：所有 `.py` 文件都应放在这个文件夹内。您也可以在打包过程中指定其他名称。您的程序将在此目录下执行。
* **主程序入口 (`app.py`)**：您的主脚本必须包含一个名为 `run()` 的函数，PySuitcase 生成的启动器将会调用它。您也可以在打包过程中指定其他名称。
* **依赖文件 (`requirements.txt`)**：列出所有第三方库，例如 `torch`、`pyqt5` 等。

#### 💡 提示 ：

如果您需要安装和使用带 GPU 支持的 PyTorch，可以在 `requirements.txt` 中这样写（以 CUDA 12.8 为例）：

```
--extra-index-url https://download.pytorch.org/whl/cu128
torch
torchvision
torchaudio
# --- 在此下方添加您的其他依赖 ---
numpy
pandas
```

另外，您需要确保您的用户已安装适合的 NVIDIA 驱动并支持此 CUDA 版本。

### 第 4 步：启动 PySuitcase 进行打包

PySuitcase 提供了两种模式：**交互式向导**和**命令行选项**。

**⚠ 首次使用前务必备份源代码，并使用交互式向导模式。**

**⚠ 命令行选项模式无二次确认，如果您的选项表明了会删除源代码，将会直接删除源代码，且无法恢复！**

#### 模式一：交互式向导模式

在您的专用命令行中，如果您不带任何参数直接运行 `pysuitcase`，它会启动交互模式。

```bash
pysuitcase
````

程序将引导您完成所有配置，包括：

  * 确认源代码文件夹和主脚本。
  * 选择是否加密代码。
  * (若不加密) 指定目标 Python 版本和架构。
  * 设置 PyPI 镜像和自定义图标。

例如：

```
> pysuitcase
Entering interactive mode...
Enter the path to your project's root directory: D:\MyAwesomeApp         \<-- 项目根目录
Encrypt Python source code for protection? [y/N]: N                      \<-- 是否进行代码加密，如果选择进行代码加密，则可以在后续选项中选择删除所有源代码
Encryption disabled. You can specify a target Python version.
Enter target Python version (Default: 3.13.5): 3.11.8                    \<-- 默认为当前环境的 Python 解释器版本
Enter target architecture (Default: amd64) (amd64, win32, arm64): amd64  \<-- 请确保您有相应的工具链，并可在当前机器上运行此架构的程序
Enter the name of your source code folder (Default: app): gfn2nmr        \<-- 源代码文件夹
Enter the name of your main script (Default: app.py): gfn2nmr_gui.py     \<-- 主程序入口（此文件必须在源代码文件夹下）
Enter the name of your requirements file (Default: requirements.txt):    \<-- 依赖文件，默认在源代码文件夹下
Do you want to use a PyPI mirror? (Recommended in some regions) [y/N]:
Enter path to a custom .ico file (or press Enter for default):           \<-- 自定义图标
Use windowless mode? [y/N]:                                              \<-- 是否使用无窗口模式
```

请注意：

  * 您的程序将在**源代码文件夹**目录下执行。
  * 无窗口模式下**不允许**用户通过控制台输入内容（例如 `input` 函数）。

在正式执行前，将列出所有的设置选项并进行二次确认。

所有流程完成后，您可以在命令行输出中看到类似这样的信息：

```
To run this again without interactive prompts, use the following command:
pysuitcase D:\MyAwesomeApp --app-folder gfn2nmr --main-script gfn2nmr_gui.py --requirements-file requirements.txt --python-version 3.11.8 --arch amd64
```

之后，您可以直接执行此命令执行代码打包。请注意，**命令行选项模式无二次确认，如果您的选项表明了会删除源代码，将会直接删除源代码，且无法恢复！**


#### 模式二：命令行选项模式

对于自动化构建，您可以使用命令行参数直接提供所有配置。

**我们强烈建议您首先通过交互式向导模式完成一次打包，然后使用向导生成的命令作为模板，在自动化工作流程中进行修改和使用。这可以有效避免因参数错误导致的意外行为。**

```bash
pysuitcase C:\path\to\MyAwesomeApp --app-folder app --main-script app.py --encrypt --icon "C:\path\to\my_icon.ico" --mirror https://pypi.tuna.tsinghua.edu.cn/simple
```

### 第 5 步：分发您的应用

打包完成后，您的项目根目录 (`MyAwesomeApp/`) 就是一个可以独立运行的完整应用。将整个文件夹压缩，就可以分发给您的用户了！

**打包后的目录结构示例：（如果使用了代码加密）**

```
MyAwesomeApp/
├── app/
│   ├── gfn2nmr_gui.cp311-win_amd64.pyd  <-- 已加密的主脚本
│   ├── model.cp311-win_amd64.pyd        <-- 已加密的模块
│   └── requirements.txt                 <-- 依赖文件，可以删除
├── python-<verison>-embed-amd64/        <-- 嵌入式 Python 环境
│   ├── python.exe
│   ├── Lib/
│   │   └── site-packages/               <-- 所有依赖库
│   └── ...
└── MyAwesomeApp.exe                     <-- 主程序启动器
```

-----

## 🙏 鸣谢

本项目的发展离不开以下开源项目的支持：

  * [**jtmoon79/PythonEmbed4Win**](https://github.com/jtmoon79/PythonEmbed4Win)：为本项目提供了下载和管理嵌入式 Python 环境的核心脚本，极大地简化了流程。

## 🚀 使用本项目的项目

  * [**GFN2NMR**](https://github.com/Wen-Xuan-Wang/GFN2NMR): 一款用于计算 C13 NMR 化学位移的科学软件。
      * 下载链接: [中文版](https://oss.diazepam.cc/gfn2nmr/gfn2nmr_zh_latest_setup.exe) | [英文版](https://oss.diazepam.cc/gfn2nmr/gfn2nmr_latest_setup.exe)

## 🧑‍💻 开发人员

  * **刘翯齐 (Heqi Liu)** - [GitHub @metaphorme](https://github.com/metaphorme/)
