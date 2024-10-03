# [BuckeyeCTF 2024 / pwn] no_handouts

> I just found a way to kill ROP. I think. Maybe?
>
> [attachment](./attachment)

## Analysis

![image](https://github.com/user-attachments/assets/6d8eb7f4-a702-4073-ac09-ad3a848a12c2)

문제에서 자체적으로 `system()`의 주소를 제공해 주고 \[1\], `v1`에 `gets()`로 입력을 받아 stack buffer overflow가 발생한다 \[2\].

## Exploitation

`system()`의 주소를 이용하여 `pop rdi; ret` 가젯과 `"/bin/sh"`의 주소도 계산할 수 있다. Canary가 없기 때문에 그대로 ROP로 `system("/bin/sh")`를 호출하면 shell을 획득할 수 있다.

[ex.py](./ex.py)

![image](https://github.com/user-attachments/assets/5c53783c-13c4-499d-9289-b4ddfcfdbeee)
