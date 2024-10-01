# \[BuckeyeCTF 2024 / beginner-pwn\] runway0

> If you've never done a CTF before, this runway should help!
>
> Hint: MacOS users (on M series) will need a x86 Linux VM. Tutorial is here: [pwnoh.io/utm](https://pwnoh.io/utm)
>
> [Attachment](./attachment)

## Analysis

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    char command[110] = "cowsay \"";
    char message[100];

    printf("Give me a message to say!\n");
    fflush(stdout);

    fgets(message, 0x100, stdin);

    strncat(command, message, 98);
    strncat(command, "\"", 2);

    system(command);
}
```

`system()`의 인자로 전달되는 `command`는 `cowsay "message"`의 형태가 되는데, `message`의 중간에 `;"`가 있으면 `cowsay "mess";age"`의 형태가 되어 command injection이 가능하다.

## Exploitation

![image](https://github.com/user-attachments/assets/d7df3aac-7bb9-4002-95a6-7d6ab8a56a85)
