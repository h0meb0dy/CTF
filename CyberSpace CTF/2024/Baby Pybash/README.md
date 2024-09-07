# [CyberSpace CTF 2024 / beginner] Baby Pybash

> I made a very secure bash terminal in Python. I don't think anyone can break in!
>
> [Attachment](./attachment)

Shell script에서 `$0`은 현재 실행 중인 스크립트 파일의 경로를 의미한다.

![image](https://github.com/user-attachments/assets/a543b6da-39a5-4de1-844d-57011a678aa2)

```bash
#!/bin/bash

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:$PATH"
cd /home/user || exit
python3 -u chall.py
```

서버에서는 bash shell에서 `chall.py`를 실행하기 때문에, 서버에 접속해서 `$0`을 입력하면 일반적인 bash shell이 실행되고, jail을 탈출하여 자유롭게 명령어를 실행할 수 있다.

![image](https://github.com/user-attachments/assets/ab363eb5-aaf4-4b89-bd72-f841d87dc1b6)
