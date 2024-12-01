import pwn
import binascii

pwn.context(arch="amd64")

shellcode = ""

# rdi == "/bin/xcalc"
shellcode += f"""
mov rax, {int(binascii.hexlify(b'lc'[::-1]), 16)}
push rax
mov rax, {int(binascii.hexlify(b'/bin/xca'[::-1]), 16)}
push rax
mov rdi, rsp
"""

# rsi == 0
shellcode += """
xor rsi, rsi
"""

# rdx == ["DISPLAY=:0", 0]
shellcode += f"""

mov rax, {int(binascii.hexlify(b':0'[::-1]), 16)}
push rax
mov rax, {int(binascii.hexlify(b'DISPLAY='[::-1]), 16)}
push rax

mov rax, rsp
mov rbx, 0
push rbx
push rax

mov rdx, rsp
"""

# rax == 0x3b (execve)
shellcode += """
mov rax, 0x3b
"""

# execve("/bin/xcalc", 0, ["DISPLAY=:0", 0])
shellcode += """
syscall
"""

shellcode = pwn.asm(shellcode)

shellcode_arr = "["
for i in range(len(shellcode)):
    shellcode_arr += hex(shellcode[i])
    if i < len(shellcode) - 1:
        shellcode_arr += ", "
    else:
        shellcode_arr += "]"

print(shellcode_arr)
