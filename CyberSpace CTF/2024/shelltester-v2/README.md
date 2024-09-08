# [CyberSpace CTF 2024 / pwnable] shelltester-v2

> Shellltester was an easy one. I changed the program. Can you solve this one?
>
> [Attachment](./attachment)

## Analysis

![image](https://github.com/user-attachments/assets/f6986c10-b483-4287-99bb-b9e2b3a9bbd1)

Format string bug \[1\]와 stack buffer overflow \[2\]가 발생한다.

## Exploitation

FSB를 이용하여 canary를 leak하고, ROP로 `system("/bin/sh")`을 호출하면 shell을 획득할 수 있다.

[ex.py](./ex.py)

![image](https://github.com/user-attachments/assets/1441153e-a48f-4332-ad0d-1e6754cbca9f)
