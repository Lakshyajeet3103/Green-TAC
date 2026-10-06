#pragma once
#include "greentac/tac.h"
#include <string>
namespace greentac {
// Generate a standalone C program. The generated main executes the TAC function
// `executions` times so benchmark timing/energy can amortize process startup.
std::string tacToC(const TACProgram& p, const std::string& functionName="program", int executions=1);
}
