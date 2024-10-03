# [BuckeyeCTF 2024 / pwn] infrequentc

> Struggling with the cryptography section? This C program can perform frequency analysis for you in the blink of an eye!
>
> [attachment](./attachment)

## Analysis

```c
	long largest = 0;
	long counts[256] = {0};
	char *text = malloc(600);
	char filepath[] = "/home/corgo/stats/stats.txt"; // default file to save to

	char *filename = strrchr(filepath,'/')+1;
...
	for(int i = 0; i < strlen(text); i++){
		counts[text[i]]++;
	}
```

`text[i]`의 type은 `char`이기 때문에 `-0x7f`부터 `0x7f`까지의 값을 가질 수 있는데, 만약 `text[i]`가 음수일 경우 OOB가 발생하여 `counts`의 앞쪽의 메모리에 접근할 수 있게 된다. 코드 상에서는 `largest`만 `counts` 앞에 있지만, 실제로 메모리에는 `largest`, `text`, `filename`, `counts` 순으로 위치한다.

![image](https://github.com/user-attachments/assets/d28ccac1-c598-4697-9066-f31aec9b0679)

## Exploitation

`filename`을 `main()`의 return address로 조작하면 마지막에 `filename`에 `fgets()`로 입력을 받을 때 `main()`의 return address를 oneshot gadget의 주소로 덮어써서 shell을 획득할 수 있다.

![image](https://github.com/user-attachments/assets/56ca3b9b-aad7-474b-bb63-6c1e719390a8)

![image](https://github.com/user-attachments/assets/62d3e6b1-2288-4db7-bf83-e58b454c5b84)

![image](https://github.com/user-attachments/assets/a2f8a1f5-c679-4d78-b150-185a85ac33f3)

그러기 위해서는 libc 주소를 먼저 leak해야 한다.

```c
	printf("The most frequent character was '%c', showing up %ld time(s).\n",(char)largest,counts[largest]);
```

`largest`를 조절하여 `counts[largest]`가 `main()`의 return address를 가리키게 만들면 `__libc_start_main()`의 주소가 출력되어 libc base를 계산할 수 있다.

[ex.py](./ex.py)

![image](https://github.com/user-attachments/assets/39f4a3d2-3ff2-4708-bbb5-f9304e9ed970)
