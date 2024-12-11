# [Platypwn 2024 / binary exploitation] BeepBoop

> A friend of mine really loves beeps and boops. Since both are equally amazing, he even built a converter to convert them into each other. To develop his programming skillz, he used Go because it’s fast and safe. But as I tried it out, something seems off!
>
> [attachment](./attachment)

## Analysis

```go
type beep [16]int

type boop [16]byte

type beepboop struct {
	beeps beep
	boops boop
}
```

```go
func convert(dest, src *[128]byte, amount int) {
	for i := range amount * 8 {
		(*dest)[i] = (*src)[i]
	}
}
```

`int` type인 `beep`의 size는 4바이트이고 `byte` type인 `boop`의 size는 1바이트인데, `convert()`에서 한 번에 8바이트씩 값을 복사하여 buffer overflow가 발생한다.

## Exploitation

Buffer overflow를 이용하여 `convertBeepBoops()`의 return address를 `sheepshoop()`의 주소로 덮어쓰면 플래그를 획득할 수 있다.

[exp.py](./exp.py)

![image](https://github.com/user-attachments/assets/6f448579-162b-420c-9ad4-2ca430f5a0b3)
