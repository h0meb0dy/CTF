# [*CTF 2019 / pwnable] oob-v8

> Yet another off by one
>
> the v8 commits is 6dc88c191f5ecc5389dc26efa3ca0907faef3598.
>
> [Attachment](./attachment)

## Setup

- Ubuntu 20.04.6 LTS (WSL)
- [6dc88c191f5ecc5389dc26efa3ca0907faef3598](https://chromium.googlesource.com/v8/v8.git/+/6dc88c191f5ecc5389dc26efa3ca0907faef3598) (2019.04.06.)

[setup.sh](./setup.sh)

## Analysis

### Patch

```diff
diff --git a/src/bootstrapper.cc b/src/bootstrapper.cc
index b027d36b5e9..ef1002fb3c9 100644
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
diff --git a/src/builtins/builtins-definitions.h b/src/builtins/builtins-definitions.h
index 04472309fc0..f113a8179c5 100644
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
index ed1e4a5c6d8..c199e3a8086 100644
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

Object array의 map을 float array의 map으로 덮어쓰면 object array에 저장된 object를 읽어올때 float number로 가져오게 된다. 이 원리로 임의의 object의 주소를 구하는 `addrof` primitive를 구현할 수 있다. 반대로, object array에 float number를 저장하고 다시 원래의 map을 복구하면 그 float number가 object의 주소가 된다. 이 원리로 임의의 주소에 fake object를 생성하는 `fakeobj` primitive를 구현할 수 있다.

### AAR / AAW

Float array의 구조를 만들고 그 위치에 fake object를 생성하면 elements 포인터를 임의의 주소로 설정하여 그 주소에 저장된 8바이트 값을 읽고 쓸 수 있다.

8바이트 AAW를 이용하여 `ArrayBuffer`의 backing store를 임의의 주소로 덮어쓰면 그 주소에 `ArrayBuffer`의 크기만큼 임의의 값을 쓸 수 있다.

![image](https://github.com/user-attachments/assets/0e7fd867-3122-47c4-9cee-e3022208f9d9)

![image](https://github.com/user-attachments/assets/73871fe3-6e7d-444d-b196-8b0d3a46e78d)

### Execute shellcode

WebAssembly instance를 생성하면 WebAssembly code를 실행하기 위해 RWX permission을 가진 메모리가 할당된다.

![image](https://github.com/user-attachments/assets/ecdb3567-0670-4c01-998c-fc2d9c6a57da)

![image](https://github.com/user-attachments/assets/8be0dc12-7338-43b8-81a8-a226e8372ce1)

이 영역에 shellcode를 쓰고 WebAssembly instance의 exported function을 실행하면 shellcode를 실행할 수 있다.

[pwn.js](./pwn.js)

![image](https://github.com/user-attachments/assets/d4853ae4-9447-475a-801d-e6518be4b09c)

[pwn.html](./pwn.html)

![image](https://github.com/user-attachments/assets/9b45934e-ddb7-4690-8d9b-a8ffc9b97525)
