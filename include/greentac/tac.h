#pragma once
#include "greentac/ast.h"
#include <string>
#include <vector>
#include <ostream>
#include <unordered_set>

namespace greentac {
enum class TACKind { Assign, Binary, Label, Goto, IfGoto };
struct TACInstruction {
    TACKind kind{TACKind::Assign};
    std::string result, arg1, arg2, op, label;
};
struct TACProgram {
    std::vector<TACInstruction> code;
    std::unordered_set<std::string> variables;
    int tempCount{0};
    std::string newTemp();
    std::string newLabel(const std::string& prefix="L");
    void print(std::ostream& os) const;
};
class TACGenerator {
public:
    TACProgram generate(const Program& p);
private:
    TACProgram out_;
    std::string genExpr(const Expr* e);
    void genStmt(const Stmt* s);
    void genBlock(const BlockStmt* b);
};
}
