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

#include <ft/bb_info.h>

using namespace ft;

BBInfo::BBInfo(BBId id,
               const std::string &functionName,
               const std::string &filename,
               const std::string &programName,
               const Lines &lines)
    : id(id), functionName(functionName), filename(filename), programName(programName), lines(lines) {}

BBInfo::BBInfo(
        BBId id, std::string &&functionName, std::string &&filename, const std::string &&programName, Lines &&lines)
    : id(id), functionName(std::move(functionName)), filename(std::move(filename)), programName(std::move(programName)),
      lines(std::move(lines)) {}

BBId BBInfo::getId() const noexcept { return id; }

const std::string &BBInfo::getFunctionName() const noexcept { return functionName; }

const std::string &BBInfo::getFilename() const noexcept { return filename; }

const std::string &BBInfo::getProgramName() const noexcept { return programName; }

const Lines &BBInfo::getLines() const noexcept { return lines; }

bool BBInfo::operator==(const BBInfo &other) const noexcept {
    return id == other.id && functionName == other.functionName && filename == other.filename &&
           programName == other.programName && lines == other.lines;
}

bool BBInfo::operator!=(const BBInfo &other) const noexcept { return !(*this == other); }
