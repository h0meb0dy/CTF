#!/bin/zsh

# install depot_tools
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git ~/depot_tools
pushd ~/depot_tools
git checkout b482a5dbbacb22770f9facecf44324aa361c4aa6
popd
echo "export PATH=\$HOME/depot_tools:\$PATH" >> ~/.zshrc
echo "export NINJA_SUMMARIZE_BUILD=1" >> ~/.zshrc
echo "export DEPOT_TOOLS_UPDATE=0" >> ~/.zshrc
source ~/.zshrc

# get v8
mkdir ~/v8
cp attachment/oob.diff ~/v8
git clone https://chromium.googlesource.com/v8/v8.git ~/v8/v8
cd ~/v8/v8
git checkout 6dc88c191f5ecc5389dc26efa3ca0907faef3598
git apply ../oob.diff

# sync submodules
cd ..
echo 'solutions = [
  {
    "name": "v8",
    "url": "https://chromium.googlesource.com/v8/v8.git",
    "deps_file": "DEPS",
    "managed": False,
    "custom_deps": {},
  },
]' > .gclient
gclient sync -D

# install dependencies
cd v8
# ./build/install-build-deps.sh --unsupported
sudo apt install -y libasound2:i386 libcap2:i386 libelf-dev:i386 libfontconfig1:i386 libglib2.0-0:i386 libgpm2:i386 libncurses5:i386 libnss3:i386 libpango1.0-0:i386 libpci3:i386 libssl-dev:i386 libssl1.1:i386 libtinfo-dev:i386 libudev1:i386 libuuid1:i386 libx11-xcb1:i386 libxcomposite1:i386 libxcursor1:i386 libxdamage1:i386 libxi6:i386 libxrandr2:i386 libxss1:i386 libxtst6:i386 linux-libc-dev:i386 ant apache2-bin autoconf binutils binutils-aarch64-linux-gnu binutils-arm-linux-gnueabihf binutils-mips64el-linux-gnuabi64 binutils-mipsel-linux-gnu bison bzip2 cdbs cmake curl dbus-x11 devscripts dpkg-dev elfutils fakeroot flex g++ g++-9-multilib g++-arm-linux-gnueabihf g++-mingw-w64-i686 gawk git-core git-svn gperf intltool lib32gcc1 lib32ncurses5-dev lib32stdc++6 lib32z1-dev libappindicator3-1 libappindicator3-dev libasound2 libasound2-dev libatk1.0-0 libatspi2.0-0 libatspi2.0-dev libbluetooth-dev libbrlapi-dev libbz2-1.0 libbz2-dev libc6 libc6-dev libc6-dev-armhf-cross libc6-i386 libcairo2 libcairo2-dev libcap-dev libcap2 libcups2 libcups2-dev libcurl4-gnutls-dev libdrm-dev libelf-dev libexpat1 libffi-dev libfontconfig1 libfreetype6 libgbm-dev libglib2.0-0 libglib2.0-dev libglu1-mesa-dev libgtk-3-0 libgtk-3-dev libjpeg-dev libkrb5-dev libnspr4 libnspr4-dev libnss3 libnss3-dev libpam0g libpam0g-dev libpango1.0-0 libpci-dev libpci3 libpcre3 libpixman-1-0 libpng16-16 libpulse-dev libpulse0 libsctp-dev libspeechd-dev libspeechd2 libsqlite3-0 libsqlite3-dev libssl-dev libstdc++6 libtinfo-dev libtool libudev-dev libudev1 libuuid1 libwayland-egl1-mesa libwww-perl libx11-6 libx11-xcb1 libxau6 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxdmcp6 libxext6 libxfixes3 libxi6 libxinerama1 libxkbcommon-dev libxrandr2 libxrender1 libxslt1-dev libxss-dev libxt-dev libxtst-dev libxtst6 linux-libc-dev-armhf-cross locales openbox p7zip patch perl pkg-config python python-crypto python-dev python-numpy python-openssl python-psutil python-yaml rpm ruby subversion texinfo uuid-dev wdiff x11-utils xcompmgr xsltproc xutils-dev xvfb xz-utils zip zlib1g gcc-arm-linux-gnueabihf g++-9-arm-linux-gnueabihf ninja-build

# install gdb plugin
echo "\nsource $HOME/v8/v8/tools/gdbinit" >> ~/.gdbinit

# build v8
gn gen out/debug --args='is_component_build=false v8_optimized_debug=false'
gn gen out/release --args='is_debug=false'
autoninja -C out/debug d8
autoninja -C out/release d8

# wabt
git clone --recursive https://github.com/WebAssembly/wabt ~/wabt
cd ~/wabt
git submodule update --init
mkdir build
cd build
cmake ..
cmake --build .
