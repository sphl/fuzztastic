// Copyright 2026 Stephan Lipp
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <filesystem>
#include <fstream>
#include <ft/io.h>
#include <iterator>
#include <stdexcept>
#include <string>

using namespace ft::io;

auto ft::io::readFile(const fs::path &filepath) -> std::string {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open file: " + filepath.string());
    }

    std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
    file.close();

    return content;
}

void ft::io::writeFile(const fs::path &filepath, const std::string &content) {
    std::ofstream file(filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open file: " + filepath.string());
    }

    file << content;
    file.close();
}
