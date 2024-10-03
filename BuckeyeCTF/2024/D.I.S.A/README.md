# [BuckeyeCTF 2024 / pwn] D.I.S.A.

> disa is the panicle of high performance and innovative design. 13bit is the future, everything else is pure cope. Embrace the performance and safety of disa
>
> [attachment](./attachment)

## Analysis

```c
void interpreter() {
    char buf[MAX_LEN];
    int16_t cells[MAX_VAL_UNSIGNED + 1];
    int16_t addr, dat = 0;
    int16_t tmp;

    while (1) {
        fgets(buf, MAX_LEN, stdin);
        
        if (strncmp(buf, "NOP", 3) == 0) {
            // nofin
        } else if (strncmp(buf, "ST", 2) == 0) {
            cells[addr] = dat;
        } else if (strncmp(buf, "LD", 2) == 0) {
            dat = cells[addr];
        } else if (strncmp(buf, "PUT", 3) == 0) {
            tmp = atoi(buf + 4);
            if (tmp >= MIN_VAL_SIGNED && tmp <= MAX_VAL_SIGNED) {
                dat = tmp;
            } else {
                puts("nuh uh uh");
            }
        } else if (strncmp(buf, "JMP", 3) == 0) {
            addr = dat;
        } else if (strncmp(buf, "ADD", 3) == 0) {
            cells[addr] += dat;
        } else if (strncmp(buf, "RD", 2) == 0) {
            printf("%d\n", dat);
        } else if (strncmp(buf, "END", 3) == 0) {
            break;
        } else {
            puts("???");
        }
    }

    puts("cya");
}
```

정의된 명령어들로 `addr`과 `dat`의 값을 조절하며 `cells`의 메모리에 접근하여 값을 읽고 쓸 수 있다.

`cells`의 크기는 `MAX_VAL_UNSIGNED + 1` (`0x2000`)인데, `addr`의 자료형은 `int16_t`이기 때문에 OOB가 발생한다.

## Exploitation

`interpreter()`의 return address를 `win()`의 주소로 덮어쓰면 되는데,

```c
        } else if (strncmp(buf, "ADD", 3) == 0) {
            cells[addr] += dat;
```

값을 쓰는 게 아니라 더하는 방식이기 때문에,

![image](https://github.com/user-attachments/assets/bbdd3bd9-f77c-431c-88df-d6681405f2cd)

결론적으로는 PIE base를 leak할 필요 없이 `interpreter()`의 return address에 `-0x312`를 더하면 된다. 따라서 `dat`는 `-0x312`가 되어야 하고,

![image](https://github.com/user-attachments/assets/3b4731c4-784c-4059-a9ab-2e3efb06e57e)

`addr`은 `0x2014`가 되어야 한다.

`addr`을 `0x2014`로 만들기 위해서는,

```c
        } else if (strncmp(buf, "LD", 2) == 0) {
            dat = cells[addr];
...
        } else if (strncmp(buf, "JMP", 3) == 0) {
            addr = dat;
```

`addr`의 초깃값이 0이기 때문에 `cells[0]`에 `0x2014`를 넣어 두고 `LD`와 `JMP`를 차례로 실행하면 되는데,

```c
        } else if (strncmp(buf, "PUT", 3) == 0) {
            tmp = atoi(buf + 4);
            if (tmp >= MIN_VAL_SIGNED && tmp <= MAX_VAL_SIGNED) {
                dat = tmp;
            } else {
                puts("nuh uh uh");
            }
...
        } else if (strncmp(buf, "ADD", 3) == 0) {
            cells[addr] += dat;
```

`dat`에는 최대 `MAX_VAL_SIGNED` (`0x1000`)까지만 넣을 수 있기 때문에, 4로 나누어서 `0x805`를 넣고 `ADD`를 4번 실행하면 된다.

[ex.py](./ex.py)

![image](https://github.com/user-attachments/assets/41f23270-9bcc-46fc-a2cc-2b2e826223d6)
