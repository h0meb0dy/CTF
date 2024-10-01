# [BuckeyeCTF 2024 / beginner-pwn] color

> What's your favorite color?
>
> [Attachment](./attachment)

## Analysis

```c
char FAVORITE_COLOR[0x20];
char FLAG[0x28];
```

전역 변수 `FAVORITE_COLOR`와 `FLAG`는 메모리 상에서 인접해 있다.

![image](https://github.com/user-attachments/assets/624ddd11-896a-434e-ae69-cc69812557fe)

따라서 `FAVORITE_COLOR`를 `0x20`바이트만큼 가득 채우면,

```c
printf("%s!?!? Mid af color\n", FAVORITE_COLOR);
```

마지막에 `FAVORITE_COLOR`를 출력할 때 `FLAG`까지 이어서 출력하게 된다.

## Exploitation

![image](https://github.com/user-attachments/assets/2a886eea-e5ec-445c-a40d-b2747515dd50)
