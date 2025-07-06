#include <windows.h>
#include <stdio.h>
#include <direct.h>

// main 函数是为 /SUBSYSTEM:CONSOLE 准备的
int main()
{
    // 这两个字符串将由 pysuitcase 在编译时动态注入
    const char *app_folder = "{{APP_FOLDER_NAME}}";
    const char *command = "{{COMMAND_STRING}}";

    // 关键步骤：在执行任何操作前，先切换到 app 目录
    if (_chdir(app_folder) != 0)
    {
        // 如果切换失败，打印错误并退出
        perror("PySuitcase Error: Could not change directory to app folder");
        return 1;
    }

    FILE *pipe;
    char buffer[1024];

    // 打开管道以运行命令并捕获输出
    if ((pipe = _popen(command, "r")) == NULL)
    {
        MessageBoxA(NULL, "Failed to execute command via _popen.", "PySuitcase Critical Error", MB_OK | MB_ICONERROR);
        return 1;
    }

    // 读取命令输出并打印到控制台
    while (fgets(buffer, sizeof(buffer), pipe) != NULL)
    {
        printf("%s", buffer);
    }

    // 关闭管道
    _pclose(pipe);

    return 0;
}