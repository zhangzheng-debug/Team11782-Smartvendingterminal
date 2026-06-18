#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "rknn_api.h"

static std::vector<unsigned char> read_file(const std::string& path) {
  std::ifstream f(path.c_str(), std::ios::binary);
  if (!f) return {};
  f.seekg(0, std::ios::end);
  size_t size = static_cast<size_t>(f.tellg());
  f.seekg(0, std::ios::beg);
  std::vector<unsigned char> data(size);
  f.read(reinterpret_cast<char*>(data.data()), size);
  return data;
}

static std::vector<std::string> read_lines(const std::string& path) {
  std::ifstream f(path.c_str());
  std::vector<std::string> lines;
  std::string line;
  while (std::getline(f, line)) {
    if (!line.empty() && line.back() == '\r') line.pop_back();
    if (!line.empty()) lines.push_back(line);
  }
  return lines;
}

static std::string json_escape(const std::string& s) {
  std::ostringstream o;
  for (char c : s) {
    switch (c) {
      case '"': o << "\\\""; break;
      case '\\': o << "\\\\"; break;
      case '\n': o << "\\n"; break;
      case '\r': o << "\\r"; break;
      case '\t': o << "\\t"; break;
      default: o << c; break;
    }
  }
  return o.str();
}

static std::string product_id_from_label(const std::string& label) {
  size_t pos = label.find('_');
  return pos == std::string::npos ? label : label.substr(0, pos);
}

static void print_error(const std::string& reason, const std::string& message) {
  std::cout << "{\"ok\":false,\"backend\":\"rknn_cli\",\"error_reason\":\""
            << json_escape(reason) << "\",\"message\":\"" << json_escape(message)
            << "\"}" << std::endl;
}

int main(int argc, char** argv) {
  std::string model_path;
  std::string input_path;
  std::string labels_path;
  int topk = 3;

  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    if (a == "--model" && i + 1 < argc) model_path = argv[++i];
    else if (a == "--input" && i + 1 < argc) input_path = argv[++i];
    else if (a == "--labels" && i + 1 < argc) labels_path = argv[++i];
    else if (a == "--topk" && i + 1 < argc) topk = std::max(1, std::atoi(argv[++i]));
  }

  if (model_path.empty() || input_path.empty() || labels_path.empty()) {
    print_error("bad_args", "missing --model/--input/--labels");
    return 2;
  }

  std::vector<unsigned char> model = read_file(model_path);
  std::vector<unsigned char> input = read_file(input_path);
  std::vector<std::string> labels = read_lines(labels_path);
  const size_t expected_size = 224 * 224 * 3;
  if (model.empty()) {
    print_error("model_read_failed", model_path);
    return 2;
  }
  if (input.size() != expected_size) {
    print_error("input_size_invalid", "expected 150528 RGB uint8 bytes");
    return 2;
  }
  if (labels.empty()) {
    print_error("labels_read_failed", labels_path);
    return 2;
  }

  rknn_context ctx = 0;
  int ret = rknn_init(&ctx, model.data(), model.size(), 0, nullptr);
  if (ret < 0) {
    print_error("rknn_init_failed", std::to_string(ret));
    return 1;
  }

  rknn_input_output_num io_num;
  memset(&io_num, 0, sizeof(io_num));
  ret = rknn_query(ctx, RKNN_QUERY_IN_OUT_NUM, &io_num, sizeof(io_num));
  if (ret < 0 || io_num.n_input < 1 || io_num.n_output < 1) {
    print_error("rknn_query_io_failed", std::to_string(ret));
    rknn_destroy(ctx);
    return 1;
  }

  rknn_input in;
  memset(&in, 0, sizeof(in));
  in.index = 0;
  in.buf = input.data();
  in.size = input.size();
  in.pass_through = 0;
  in.type = RKNN_TENSOR_UINT8;
  in.fmt = RKNN_TENSOR_NHWC;

  auto t0 = std::chrono::steady_clock::now();
  ret = rknn_inputs_set(ctx, 1, &in);
  if (ret < 0) {
    print_error("rknn_inputs_set_failed", std::to_string(ret));
    rknn_destroy(ctx);
    return 1;
  }
  ret = rknn_run(ctx, nullptr);
  if (ret < 0) {
    print_error("rknn_run_failed", std::to_string(ret));
    rknn_destroy(ctx);
    return 1;
  }

  std::vector<rknn_output> outputs(io_num.n_output);
  memset(outputs.data(), 0, sizeof(rknn_output) * outputs.size());
  outputs[0].want_float = 1;
  ret = rknn_outputs_get(ctx, io_num.n_output, outputs.data(), nullptr);
  auto t1 = std::chrono::steady_clock::now();
  if (ret < 0) {
    print_error("rknn_outputs_get_failed", std::to_string(ret));
    rknn_destroy(ctx);
    return 1;
  }

  int count = outputs[0].size / sizeof(float);
  float* vals = reinterpret_cast<float*>(outputs[0].buf);
  std::vector<int> idx(count);
  for (int i = 0; i < count; ++i) idx[i] = i;
  std::sort(idx.begin(), idx.end(), [&](int a, int b) { return vals[a] > vals[b]; });
  topk = std::min(topk, count);
  long latency_ms = std::chrono::duration_cast<std::chrono::milliseconds>(t1 - t0).count();

  std::cout << "{\"ok\":true,\"backend\":\"rknn_cli\",\"npu\":true";
  std::cout << ",\"latency_ms\":" << latency_ms;
  std::cout << ",\"model_version\":\"v263_rknn_10sku_baseline\"";
  std::cout << ",\"top1\":";
  int i0 = idx.empty() ? 0 : idx[0];
  std::string label0 = (i0 < static_cast<int>(labels.size())) ? labels[i0] : std::to_string(i0);
  std::cout << "{\"class_index\":" << i0 << ",\"product_id\":\"" << json_escape(product_id_from_label(label0))
            << "\",\"label\":\"" << json_escape(label0) << "\",\"confidence\":" << vals[i0] << "}";
  std::cout << ",\"top3\":[";
  for (int r = 0; r < topk; ++r) {
    int ix = idx[r];
    std::string label = (ix < static_cast<int>(labels.size())) ? labels[ix] : std::to_string(ix);
    if (r) std::cout << ",";
    std::cout << "{\"rank\":" << (r + 1) << ",\"class_index\":" << ix
              << ",\"product_id\":\"" << json_escape(product_id_from_label(label))
              << "\",\"label\":\"" << json_escape(label)
              << "\",\"confidence\":" << vals[ix] << "}";
  }
  std::cout << "],\"error_reason\":null}" << std::endl;

  rknn_outputs_release(ctx, io_num.n_output, outputs.data());
  rknn_destroy(ctx);
  return 0;
}
