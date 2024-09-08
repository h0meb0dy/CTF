# [CyberSpace CTF 2024 / beginner] ticket-bot

> Welcome to TicketBot v1.0. Open a ticket and we will help you asap!
>
> [Attachment](./attachment)

## Analysis

![image](https://github.com/user-attachments/assets/4bc1e606-dbab-47e7-b10f-3de8a845a9ab)

`init()`에서 `srand()`의 인자로 들어가는 `seed`는 10,000,000보다 작은 값이기 때문에 충분히 브루트포싱이 가능하다.

![image](https://github.com/user-attachments/assets/3ed43f79-7f2c-44ca-a9c0-29a665eac173)

`seed`를 브루트포싱하여 `password`를 맞춰서 `AdminMenu()`로 들어가면 Stack buffer overflow \[1\]와 Format string bug \[2\]를 이용할 수 있다.

## Exploitation

FSB를 이용하여 PIE base를 leak하고, 바이너리의 가젯을 사용하여 ROP로 libc base를 leak한 뒤에 `system("/bin/sh")`을 호출하면 shell을 획득할 수 있다.

[ex.py](./ex.py)

![image](https://github.com/user-attachments/assets/3b1ee1c8-06ca-41b7-ae8a-a31928c62303)
