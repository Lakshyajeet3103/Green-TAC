#pragma once
#include "greentac/tac.h"
#include <map>
#include <string>

namespace greentac {
struct Features {
    double instructions{0};
    double binary_ops{0};
    double branches{0};
    double labels{0};
    double temporaries{0};
    double memory_ops{0};
    double comparisons{0};
    double basic_blocks{0};
    double max_expr_depth{0};
    double common_subexpressions{0};
};
Features extractFeatures(const TACProgram& p);
std::map<std::string,double> featureMap(const Features& f);
}
