with open("pwn.wasm", "rb") as f:
    wasm = f.read()

wasm_code = "["

for i in range(len(wasm)):
    wasm_code += hex(wasm[i])
    if i < len(wasm) - 1:
        wasm_code += ", "
    else:
        wasm_code += "]"

print(wasm_code)
