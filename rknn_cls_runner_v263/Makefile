SDK_ROOT ?= /root/qsm_sdk/rk3568_linux_r60_v1.3.2_qsm368zp-QSM368ZP_rl
CXX ?= $(SDK_ROOT)/prebuilts/gcc/linux-x86/aarch64/gcc-arm-10.3-2021.07-x86_64-aarch64-none-linux-gnu/bin/aarch64-rockchip1031-linux-gnu-g++
RKNN_API_DIR ?= $(SDK_ROOT)/external/rknpu2/runtime/RK356X/Linux/librknn_api
CXXFLAGS ?= -O2 -std=c++11 -Wall -Wextra
LDFLAGS ?= -L$(RKNN_API_DIR)/aarch64 -lrknnrt
INCLUDES ?= -I$(RKNN_API_DIR)/include

all: vision_rknn_cli

vision_rknn_cli: src/main.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) $< -o $@ $(LDFLAGS)

clean:
	rm -f vision_rknn_cli

