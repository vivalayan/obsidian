### 前置准备

#### Set-UID程序：
- set-uid程序是在计算机系统中具有特殊权限的一种程序。当一个可执行文件具有set-uid权限时，它在执行时可以暂时获得与其所有者或特定用户相关联的特权级别。
- set-uid代表"Set User ID"，是Unix和类Unix操作系统中的一个概念。当用户执行一个具有set-uid权限的程序时，该程序将在执行期间暂时获得与文件所有者或指定用户相关联的权限。这意味着即使用户自身没有特权，他们也可以以特权身份执行该程序。
- 这种特权级别的提升允许普通用户执行某些需要特权访问的任务，例如管理系统配置、访问受限资源或执行系统级操作。set-uid程序通常用于提供特定功能和服务，同时确保仅在必要时才提升权限，以减少潜在的安全风险。

### Task 1 Manipulating Environment Variables

本实验要求打印出系统的环境变量，我们直接采用printenv命令打印即可：

![[Pasted image 20231104205005.png]]

采用 printenv PWD：

![[Pasted image 20231104205203.png]]

使用 export 和 unset 来设置或取消设置环境变量。 需要注意的是，这两个命令不是单独的程序； 它们是 Bash 的两个内部命令（无法在 Bash 之外找到它们）。可以看到在fish shell内部不存在unset指令。我们人为指定test变量后又利用unset将其取消，其最终结果与我们的预期相符合。

![[Pasted image 20231104205306.png]]
### Task 2 Passing Environment Variables from Parent Process to Child Process

#### Step 1. 编译并运行以下程序

首先运行父进程，将输出保存到file1中

![[Pasted image 20231104210010.png]]

然后再运行子进程，并将输出保存到file2中：

![[Pasted image 20231104210117.png]]

最后我们对比file1和file2两者差异：

![[Pasted image 20231104210151.png]]

diff命令没有产生输出，代表二者相同。
### Task 3 Environment Variables and `execve()`




### Task 4 Environment Variables and `system()`

### Task 5 Environment Variables and `set-UID` Programs

### Task 6 The PATH Environment Variable and `Set-UID` Programs

### Task 7 The `LD_PRELOAD` Environment Variable and `Set-UID` Programs