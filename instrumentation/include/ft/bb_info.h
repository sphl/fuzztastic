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

#include <functional>
#include <set>
#include <string>
#include <utility>

namespace ft {

using BBId = unsigned long;

using LineNumber = unsigned long;
using Lines = std::set<LineNumber>;

/**
 * A simple data class that holds relevant basic block (BB) information.
 */
class BBInfo {
  private:
    BBId id;
    std::string functionName;
    std::string filename;
    Lines lines;

  public:
    BBInfo(BBId id, const std::string &functionName, const std::string &filename, const Lines &lines);
    BBInfo(BBId id, std::string &&functionName, std::string &&filename, Lines &&lines);
    BBInfo(const BBInfo &other) = default;
    BBInfo(BBInfo &&other) = default;
    BBInfo &operator=(const BBInfo &other) = default;
    BBInfo &operator=(BBInfo &&other) = default;
    ~BBInfo() = default;

    [[nodiscard]] BBId getId() const noexcept;
    [[nodiscard]] const std::string &getFunctionName() const noexcept;
    [[nodiscard]] const std::string &getFilename() const noexcept;
    [[nodiscard]] const Lines &getLines() const noexcept;

    bool operator==(const BBInfo &other) const noexcept;
    bool operator!=(const BBInfo &other) const noexcept;
};

}  // namespace ft