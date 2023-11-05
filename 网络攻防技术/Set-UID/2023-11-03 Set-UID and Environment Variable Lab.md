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

#### Step 2. 编译并运行以下程序

然后再运行子进程，并将输出保存到file2中：

![[Pasted image 20231104210117.png]]

最后我们对比file1和file2两者差异：

![[Pasted image 20231104210151.png]]

diff命令没有产生输出，代表二者相同。
### Task 3 Environment Variables and `execve()`

#### Step 1. 描述程序运行结果

这个程序只是执行一个名为/usr/bin/env 的程序，它打印出当前进程的环境变量。发现执行结果为空。

![[Pasted image 20231104210743.png]]

我们查看execve函数的定义，其参数解释如下：

![[Pasted image 20231104210924.png]]

- 第一个参数为一个可执行的有效的路径名。第二个参数argv系利用数组指针来传递给执行文件，v是要调用的程序执行的参数序列，也就是我们要调用的程序需要传入的参数；envp则为传递给执行文件的新环境变量数。
- 所以在此处，我们赋予新进程的环境变量为空，自然印出环境变量结果为空。

#### Step 2. 修改程序后，描述程序运行结果

任务：将第①行中 execve() 的调用更改为以下内容； 描述你的观察。

![[Pasted image 20231104211121.png]]

结论：修改后，execve打印的环境变量为本机真实的环境变量，这也是extern变量environ所指向的环境变量数组。同时，execve()产生的新进程的环境变量需要在调用时进行传递。
### Task 4 Environment Variables and `system()`

通过阅读Linux Manual，我们知道system()通过调用fork()函数新建一个子进程；在子进程中调用execl()函数去执行command；在父进程中调用wait去等待子进程结束。

![[Pasted image 20231104211504.png]]

![[Pasted image 20231104211616.png]]
### Task 5 Environment Variables and `set-UID` Programs

#### Step 1 编写以下程序

![[Pasted image 20231104212340.png]]

![[Pasted image 20231104212431.png]]

#### Step 2 将其所有权改为root，并使其成为Set-UID程序

直接采用chown和chmod来修改权限：

![[Pasted image 20231104212610.png]]

#### Step 3 在shell 中使用 export 命令设置以下环境变量:

我们通过export来人为设定一些环境变量，然后执行我们编写的程序。结果为我们人工添加的环境变量已经被插入到了系统环境变量中。

![[Pasted image 20231104213040.png]]
### Task 6 The PATH Environment Variable and `Set-UID` Programs

编写两个版本的ls程序，一个为恶意程序，另一个为普通的通过system函数来执行的ls程序：

![[Pasted image 20231104213823.png]]

将task6程序设定为Set-UID程序并运行：

![[Pasted image 20231104214025.png]]

接下来我们修改系统的环境变量，将PATH修改为当前文件夹路径，然后将我们的恶意ls程序编译输出为ls，以达到欺骗system函数的目的：

![[Pasted image 20231104214242.png]]

此时还需要修改链接，将sh指向zsh，才能达到我们的攻击目的。

![[Pasted image 20231104214443.png]]

看到此时task6中的system函数执行结果为我们预先设定的结果，这说明我们成功欺骗了system函数，使得其采用了我们编写的ls程序。
### Task 7 The `LD_PRELOAD` Environment Variable and `Set-UID` Programs

首先构造我们自己的库函数mylib.c

![[Pasted image 20231104214943.png]]

然后我们将其编译为动态链接库。重新执行myprog程序，发现其中的sleep函数已经变为了我们自己编写的库中的函数，说明攻击成功。

![[Pasted image 20231104214920.png]]

接下来我们让myprog变为Set-UID程序，然后以普通用户的身份运行它：

![[Pasted image 20231104215326.png]]

发现其正常休眠一秒钟，然后将控制权交回shell。接下来我们再在root用户中设置LD_PRELOAD环境变量，然后再次运行myprog：

![[Pasted image 20231104215656.png]]

此时输出仍然是恶意版本的sleep函数的输出。退出root用户登录，我们用普通用户再次执行myprog时，仅仅休眠一秒。这说明root用户设置的环境变量仅仅局限于root用户自己能够访问。

![[Pasted image 20231104215812.png]]

接下来我们添加一个用户user1，然后将myprog的所有权转移给user1。在root的情况下导出环境变量，并切换到普通用户级别。运行myprog程序过后发现并未出现预期情况，仅仅是sleep一秒。

![[Pasted image 20231105005332.png]]

现在自行编写一个print_env来输出环境变量，同时考虑到父进程与子进程的区别。首先注释子进程，用父进程的环境变量，并将输出重定向至parent1.txt中。

![[Pasted image 20231105011711.png]]

然后用相同的方法，得到子进程的环境变量，保存在child1.txt中

![[Pasted image 20231105011808.png]]

查看两生成文件的不同，发现二者i相同。这说明子进程与父进程环境变量相同，且含LD_PRELOAD，即子进程继承了用户进程的LD_PRELOAD环境变量。

![[Pasted image 20231105012038.png]]

接下来按照同样的方法，以子进程与父进程为区别，将print_env设置为root所有的Set-UID程序，以普通用户的权限来更改环境变量。

![[Pasted image 20231105012559.png]]

![[Pasted image 20231105012650.png]]

然后查看二者不同。可以得到结论，父进程的环境变量可以发现LD_PRELOAD环境变量，而在子进程的环境变量中找不到，即子进程没有继承用户进程的LD_PRELOAD环境变量。

![[Pasted image 20231105012746.png]]

将print_env程序设定为所有者为root的Set-UID 程序。以root用户更改环境变量，分别以root用户和seed用户执行程序。

![[Pasted image 20231105012954.png]]

将输出保存至parent3.txt

![[Pasted image 20231105013035.png]]

然后按照同样的操作对子进程进行操作：

![[Pasted image 20231105013133.png]]

最后对比生成文件的差异，发现子进程与父进程环境变量相同，且含LD_PRELOAD，即子进程继承了用户进程的LD_PRELOAD环境变量。

![[Pasted image 20231105013250.png]]

然后以普通用户的权限运行（直接截在一张图上），发现父进程的环境变量可以发现LD_PRELOAD环境变量，而在子进程的环境变量中找不到，即子进程没有继承用户进程的LD_PRELOAD环境变量。

![[Pasted image 20231105013643.png]]

最后将printenv修改为所有者为user1的Set-UID程序，以seed用户的身份执行：

![[Pasted image 20231105014110.png]]

父进程的环境变量可以发现LD_PRELOAD环境变量，而在子进程的环境变量中找不到，即子进程没有继承用户进程的LD_PRELOAD环境变量。

造成这种现象出现的主要原因为动态链接器的保护机制。当运行进程的真实用户ID与程序的拥有者的用户ID不一致时，进程会忽略掉父进程的LD_PRELOAD环境变量；若ID一致，则子进程会继承此时运行进程的真实用户下的LD_PRELOAD环境变量，并加入共享库。
### Task 8 Invoking External Programs Using `system()` versus `execve()`

以root身份新创建一个目录test8，然后在该目录下新建test.txt，发现以普通用户的权限test.txt不可写。

![[Pasted image 20231105103041.png]]

编译以下程序，使其成为一个root拥有的Set-UID程序。 该程序将使用 system() 来调用该命令。

![[Pasted image 20231105103333.png]]

通过catall得到了root权限的shell，成功删除test.txt。然后注释掉system(command)语句，取消execve()语句； 程序将使用 execve() 来调用命令。

![[Pasted image 20231105103424.png]]

攻击失败。因为execve会执行一个新程序，而不会调用新的shell程序。

![[Pasted image 20231105103521.png]]

以root用户创建一个etc文件夹，文件夹内创建zzz文件，并设置其权限为0644。

![[Pasted image 20231105103719.png]]

更改cap_leak.c下zzz的路径

![[Pasted image 20231105103824.png]]

编译cap_leak.c，设置为Set-UID root程序。









### Task 9 Capability Leaking