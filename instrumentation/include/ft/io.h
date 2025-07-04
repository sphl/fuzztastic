// Copyright 2021-2025 Chair for Software & Systems Engineering, TUM
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

#pragma once

#include <filesystem>
#include <string>

namespace fs = std::filesystem;

namespace ft::io {

/**
 * Reads the content of a file.
 */
std::string readFile(const fs::path &filepath);

/**
 * Writes the given content to a file.
 */
void writeFile(const fs::path &filepath, const std::string &content);

}  // namespace ft::io