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

#include <ft/bb_info.h>
#include <string>
#include <vector>

namespace ft::formatter {

/**
 * Returns the basic block (BB) information as a JSON string.
 */
auto toJSON(const std::vector<BBInfo> &bbInfos) -> std::string;

}  // namespace ft::formatter