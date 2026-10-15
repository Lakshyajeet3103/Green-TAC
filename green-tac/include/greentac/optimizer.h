#pragma once
#include "greentac/tac.h"
#include <string>

namespace greentac {
enum class Strategy { Baseline, Lightweight, DAG };
std::string strategyName(Strategy s);
TACProgram optimize(const TACProgram& input, Strategy s);
}
