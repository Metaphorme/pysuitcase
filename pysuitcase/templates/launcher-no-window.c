#include <windows.h>
#include <stdio.h>

void RedirectIOToParentConsole();
BOOL RunCommandHidden(char *command);

// WinMain 是为 /SUBSYSTEM:WINDOWS 准备的
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
{
    // 这两个字符串将由 pysuitcase 在编译时动态注入
    const char app_folder[] = "{{APP_FOLDER_NAME}}";
    char command[] = "{{COMMAND_STRING}}"; // 可写，因为 CreateProcessA 可能修改它

    // 关键步骤：在执行任何操作前，先切换到 app 目录
    if (!SetCurrentDirectoryA(app_folder))
    {
        MessageBoxA(NULL, "Could not change directory to app folder.", "PySuitcase Critical Error", MB_OK | MB_ICONERROR);
        return 1;
    }

    // 尝试附加到父进程的控制台
    if (AttachConsole(ATTACH_PARENT_PROCESS))
    {
        RedirectIOToParentConsole();

        // system() 会在当前目录（我们已经切换好了）执行命令
        int exit_code = system(command);

        FreeConsole();
        return exit_code;
    }
    else
    {
        // 在后台静默执行命令
        if (!RunCommandHidden(command))
        {
            MessageBoxA(NULL, "Failed to create process in hidden mode.", "PySuitcase Critical Error", MB_OK | MB_ICONERROR);
            return 1;
        }
        return 0;
    }
}

void RedirectIOToParentConsole()
{
    FILE *fp;
    freopen_s(&fp, "CONOUT$", "w", stdout);
    freopen_s(&fp, "CONOUT$", "w", stderr);
    freopen_s(&fp, "CONIN$", "r", stdin);
}

BOOL RunCommandHidden(char *command)
{
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESTDHANDLES;
    si.hStdInput = NULL;
    si.hStdOutput = NULL;
    si.hStdError = NULL;

    ZeroMemory(&pi, sizeof(pi));

    // CreateProcess 会在当前目录（我们已经切换好了）执行命令
    BOOL success = CreateProcessA(
        NULL, command, NULL, NULL, FALSE,
        CREATE_NO_WINDOW,
        NULL, NULL, &si, &pi);

    if (success)
    {
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    }

    return success;
}