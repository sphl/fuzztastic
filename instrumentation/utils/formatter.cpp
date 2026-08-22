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

#include <ft/bb_info.h>
#include <ft/formatter.h>
#include <rapidjson/stringbuffer.h>
#include <rapidjson/writer.h>
#include <string>
#include <vector>

using namespace ft;
using namespace ft::formatter;

auto ft::formatter::toJSON(const std::vector<BBInfo> &bbInfos) -> std::string {
    rapidjson::StringBuffer buffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);

    writer.StartArray();
    for (const auto &bbInfo : bbInfos) {
        writer.StartObject();
        writer.Key("id");
        writer.Uint64(bbInfo.getId());
        writer.Key("function");
        writer.String(bbInfo.getFunctionName().c_str());
        writer.Key("program");
        writer.String(bbInfo.getProgramName().c_str());
        writer.Key("file");
        writer.String(bbInfo.getFilepath().c_str());
        writer.Key("lines");
        writer.StartArray();
        for (const auto &line : bbInfo.getLines()) {
            writer.Uint64(line);
        }
        writer.EndArray();
        writer.EndObject();
    }
    writer.EndArray();

    return buffer.GetString();
}
