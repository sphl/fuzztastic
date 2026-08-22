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

#pragma once

#include <set>
#include <string>

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
    std::string filepath;
    std::string programName;
    Lines lines;

  public:
    BBInfo(BBId id,
           const std::string &functionName,
           const std::string &filepath,
           const std::string &programName,
           const Lines &lines);
    BBInfo(BBId id, std::string &&functionName, std::string &&filepath, const std::string &&programName, Lines &&lines);
    BBInfo(const BBInfo &other) = default;
    BBInfo(BBInfo &&other) = default;
    auto operator=(const BBInfo &other) -> BBInfo & = default;
    auto operator=(BBInfo &&other) -> BBInfo & = default;
    ~BBInfo() = default;

    [[nodiscard]] auto getId() const noexcept -> BBId;
    [[nodiscard]] auto getFunctionName() const noexcept -> const std::string &;
    [[nodiscard]] auto getFilepath() const noexcept -> const std::string &;
    [[nodiscard]] auto getProgramName() const noexcept -> const std::string &;
    [[nodiscard]] auto getLines() const noexcept -> const Lines &;

    auto operator==(const BBInfo &other) const noexcept -> bool;
    auto operator!=(const BBInfo &other) const noexcept -> bool;
};

}  // namespace ft