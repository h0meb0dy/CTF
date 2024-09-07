# [CyberSpace CTF 2024 / pwnable] ticket-bot-v2

> Welcome to TicketBot v2.0. We fixed some bugs and added some extra feature!
>
> [Attachment](./attachment)

## Logging in as admin

![image](https://github.com/user-attachments/assets/74aa4a61-a23e-4f3e-90e6-5288e3bf5427)

`tickets`에는 최대 5개의 ticket을 저장할 수 있고, 바로 뒤쪽에는 `seed`, `password`, `currentticketid`가 차례로 저장되어 있다.

![image](https://github.com/user-attachments/assets/31227285-da3c-4da5-87d2-49bdc8e98029)

`ticketcounter`가 5보다 큰 경우에 0으로 초기화하는데, `tickets`의 최대 index는 4이기 때문에 `ticketcounter`가 5인 경우에 OOB가 발생한다. 이를 이용하여 `password`를 임의의 값으로 덮어쓸 수 있고, admin으로 로그인할 수 있다.

## Exploiting BOF / FSB

![image](https://github.com/user-attachments/assets/228f5711-2dae-404c-8f72-f1b35a95834f)

![image](https://github.com/user-attachments/assets/471389be-8698-43b0-9e15-635a2e001444)

Admin으로 로그인했을 때 진입할 수 있는 `adminpass()`에서 stack buffer overflow \[1\]와 format string bug \[2\]가 발생한다.

FSB를 이용하여 스택에 있는 canary와 PIE 주소를 leak하고, 바이너리에 있는 가젯들을 활용하여 libc 주소까지 leak할수 있다. 그리고 나서 `system("/bin/sh")`를 호출하면 shell을 획득할 수 있다.

[ex.py](./ex.py)

![image](https://github.com/user-attachments/assets/e752b501-d9c4-4c07-af1b-1d769c3a194b)
