#pragma once
#include <cstdint>
#include <string>
#include <optional>

namespace greentac {
class RaplReader {
public:
    RaplReader();
    bool available() const { return available_; }
    std::optional<double> readPackageEnergyJ() const;
    const std::string& source() const { return source_; }
private:
    bool available_{false};
    std::string energyPath_;
    std::string source_;
};
}
