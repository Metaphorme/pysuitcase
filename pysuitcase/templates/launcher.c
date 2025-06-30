#include <windows.h>
#include <stdio.h>

#define BUFFER_SIZE 1024

void run_command_and_capture_output(const char *command)
{
    FILE *pipe;
    char buffer[BUFFER_SIZE];

    // 打开管道以运行命令并捕获输出
    if ((pipe = _popen(command, "r")) == NULL)
    {
        // 在极端情况下，用弹窗显示错误
        MessageBoxA(NULL, "Failed to execute command via _popen.", "PySuitcase Critical Error", MB_OK | MB_ICONERROR);
        exit(1);
    }

    // 读取命令输出并打印到控制台
    while (fgets(buffer, BUFFER_SIZE, pipe) != NULL)
    {
        printf("%s", buffer);
    }

    // 关闭管道
    _pclose(pipe);
}

int main()
{
    // 这个命令字符串将由 pysuitcase 在编译时动态注入
    const char *command = "{{COMMAND_STRING}}";
    run_command_and_capture_output(command);
    return 0;
}