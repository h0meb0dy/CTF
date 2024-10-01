# [BuckeyeCTF 2024 / beginner-pwn] runway1

> Starting to ramp up!
>
> [Attachment](./attachment)

## Analysis

```c
int win() {
    printf("You win! Here is your shell:\n");

    system("/bin/sh");
}

int get_favorite_food() {
    char food[64];

    printf("What is your favorite food?\n");
    fflush(stdout);

    fgets(food, 100, stdin);

    printf("Hmmm..... %s...", food);
}
```

`get_favorite_food()`에서 64바이트 크기의 `food`에 100바이트를 입력받아 stack buffer overflow가 발생한다.

## Exploitation

PIE와 canary가 없기 때문에 `get_favorite_food()`의 return address를 `win()`의 주소로 덮어쓰면 shell을 획득할 수 있다.

[ex.py](./ex.py)

![image](https://github.com/user-attachments/assets/04c68d72-c8ba-45f6-8cd1-7c69fc85a908)
