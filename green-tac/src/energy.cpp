#include "greentac/energy.h"
#include <filesystem>
#include <fstream>
#include <regex>
#include <sstream>
#include <cstdlib>

namespace fs=std::filesystem;
namespace greentac {
RaplReader::RaplReader(){
#ifdef __linux__
    const fs::path root("/sys/class/powercap");
    if(fs::exists(root)){
        for(const auto& e:fs::directory_iterator(root)){
            auto p=e.path()/"energy_uj";
            if(fs::exists(p)){energyPath_=p.string();available_=true;source_="Linux powercap RAPL: "+energyPath_;break;}
        }
    }
#endif
    if(!available_)source_="Unavailable (no supported Linux powercap/RAPL energy_uj counter found)";
}
std::optional<double> RaplReader::readPackageEnergyJ() const{
    if(!available_) return std::nullopt;
    std::ifstream in(energyPath_);
    long double uj=0;
    if(!(in>>uj)) return std::nullopt;
    return static_cast<double>(uj/1e6L);
}
}
