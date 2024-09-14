# [Urmia CTF 2024 / pwnable] Look-up

> Unravel the hidden messages buried in the echoes of code.
>
> [Attachment](./attachment)

## Analysis

![image](https://github.com/user-attachments/assets/f79e59e0-451a-478a-8cc2-4819d4003f77)

Stack buffer overflow \[1\] 가 발생한다. `read()`로 입력을 받고 `printf("%s")`로 출력하기 때문에 \[2\] 스택에 저장된 값들을 leak할 수 있다. `s`에 `"UCTF"`라는 문자열이 포함되어 있으면 `vuln()`을 다시 호출하여 \[3\] stack BOF를 반복적으로 이용할 수 있다.

## Exploitation

### Leak PIE

![image](https://github.com/user-attachments/assets/4b1c737a-30d4-4a50-88cb-e9f5e6994ce1)

`s`에 `0x1a`바이트를 입력하면 `vuln()`의 return address를 leak하여 PIE base를 계산할 수 있다.

### Leak canary

![image](https://github.com/user-attachments/assets/0f1758e7-eeeb-4918-85e6-72df9d255e3a)

`s`에 `0xb`바이트를 입력하여 canary의 null byte를 덮어쓰면 canary까지 출력되어 나온다.

이후 `vuln()`의 return address를 `win()`의 주소로 덮어쓰면 shell을 획득할 수 있다.

[ex.py](./ex.py)

![image](https://github.com/user-attachments/assets/1dc5e27b-1917-4fa4-9e8d-0d5f96ef49c8)
