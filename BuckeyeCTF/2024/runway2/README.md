# [BuckeyeCTF 2024 / beginner-pwn] runway2

> Now with a twist!
>
> [attachment](./attachment)

## Analysis

```c
int get_answer() {
    char answer[16];

    fgets(answer, 0x40, stdin);

    return strtol(answer, NULL, 10);
}
```

`0x10`바이트 크기의 `answer`에 `0x40`바이트만큼 입력받아 Stack buffer overflow가 발생한다.

## Exploitation

```c
int win(int check, int mate) {
    if (check == 0xc0ffee && mate == 0x007ab1e) {
        printf("You win! Here is your shell:\n");
        fflush(stdout);

        system("/bin/sh");
    } else {
        printf("No way!");
        fflush(stdout);
    }
}
```

ROP로 `win(0xc0ffee, 0x7ab1e)`을 호출하면 shell을 획득할 수 있다.

[ex.py](./ex.py)

![image](https://github.com/user-attachments/assets/e703a2d8-c112-4dbe-bf2f-68f52b93eda5)
