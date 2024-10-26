# [Whitehat Conference 2024 Quals / pwnable] gf

> [attachment](./attachment)

## Analysis

![image](https://github.com/user-attachments/assets/61f6b574-0490-4803-ac5b-622c587b491a)

![image](https://github.com/user-attachments/assets/80e704cb-a59d-409e-a5be-087945e7e49e)

BSS의 `src`에 `0xbc`바이트를 입력받고 \[1\], stack의 `dest`에 `0xbb`바이트를 `memcpy()`로 복사하여 \[2\] stack buffer overflow가 발생한다. Canary가 없기 때문에 ROP가 가능하다.

`memcpy()`에서 애매하게 `0xbb`바이트를 복사하는 이유를 알기 위해 `memcpy()` 이후의 stack 메모리를 보면,

![image](https://github.com/user-attachments/assets/9a36e15b-63dc-4c0c-a2c6-ec9a2e9b53cb)

libc 주소의 상위 3바이트가 저장되어 있는 것을 확인할 수 있다. Libc 주소의 하위 1.5바이트는 고정이기 때문에 중간의 1.5바이트만 brute force하면 libc의 임의 주소로 한 번 return할 수 있다.

## Exploitation

### First attempt (failed)

`main()`이 return하는 시점에서 `rdi`에 `memcpy()`의 첫 번째 인자인 `dest`가 그대로 남아 있다.

![image](https://github.com/user-attachments/assets/834ca052-fa93-4c40-ac16-06a246bd9a12)

`rdi`에 `/bin/sh`를 넣고 `system()`으로 return하면 shell을 획득할 수 있을 것이라고 예상했지만, 실제로는 `rdi`가 stack 주소이기 때문에 `system()`이 호출되는 과정에서 이 값이 overwrite되어 실패하였다.

### Second attempt

![image](https://github.com/user-attachments/assets/f53417d6-392d-4565-8627-355b3246da90)

`rbp`는 `main()`의 SFP를 덮어쓰거나 `pop rbp; ret` gadget을 이용하여 어떻게든 control이 가능하기 때문에, `rax`만 0으로 맞추면 이 oneshot gadget을 사용할 수 있다.

> [setvbuf(3p) - Linux manual page](https://man7.org/linux/man-pages/man3/setvbuf.3p.html)
>
> Upon successful completion, setvbuf() shall return 0.

내부 로직에는 관심이 없지만, 어쨌든 `setvbuf()`를 호출하면 `rax`가 0으로 설정되는 것을 확인하였다.

[ex.py](./ex.py)

![image](https://github.com/user-attachments/assets/094ec5fb-febd-4f6c-a68b-6eb50c01e5bb)

![image](https://github.com/user-attachments/assets/c8ea8da2-133a-4bdd-9c53-f4abeb23fcf3)
