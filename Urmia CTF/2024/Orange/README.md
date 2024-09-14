# [Urmia CTF 2024 / pwnable] Orange

> Dive into the juicy depths of this challenge and see if you can squeeze out a surprise.
>
> [Attachment](./attachment)

## Analysis

![image](https://github.com/user-attachments/assets/9adae22f-ff11-4d1f-8744-d343b8b2608e)

![image](https://github.com/user-attachments/assets/a794f927-ef55-443e-b4ea-5f098f5af13d)

`set_buyer_name()`에서 Stack buffer overflow \[1\], `show_cart()`에서 format string bug \[2\] 가 발생한다.

## Exploitation

FSB를 이용하여 canary와 스택 주소를 leak한 뒤에, 스택에 실행 권한이 있는 것을 이용하여 스택에 shellcode를 넣고 return address를 shellcode의 주소로 덮어쓰면 shell을 획득할 수 있다.

[ex.py](./ex.py)

![image](https://github.com/user-attachments/assets/578f57f5-965f-4843-8eed-121a1791a6bc)
